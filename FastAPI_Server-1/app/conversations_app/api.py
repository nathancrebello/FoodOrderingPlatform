import json
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from .models import Conversation, RequestBody
from .schemas import OrderOutput
from app.utils.db_base import get_db
from app.settings import logger, OPENAI_KEY
from sqlalchemy import nulls_last, func
import os
import pandas as pd
from wonderwords import RandomWord
from datetime import datetime, timezone
from sqlalchemy import Integer
import openai
from openai import AsyncOpenAI
from better_profanity import profanity
conversation_router = APIRouter()


# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_KEY)


# Load menu once at module level
menu_path = os.path.join(os.path.dirname(__file__), 'menu.csv')
df = pd.read_csv(menu_path)
menu_string = df.set_index("Item").apply(
    lambda row: {"sizes": row["Size Options"].split(","), "toppings": row["Topping Options"].split(",")}, axis=1
).to_dict()


# System prompt for the order processing
SYSTEM_PROMPT = """You are a highly skilled waiter processing customer orders according to these strict rules:


1. MENU VALIDATION:
- ONLY accept items that align with the provided menu.
- Ignore items that do not align with given menu.

2. SIZE HANDLING:
- Use '?' only for items whose size isn't specified by customer.
- Use '!' only when customer requests an unavailable size for an item that exists in menu.
- Use 'One Size Option' only for items that have exactly one size option in the menu.
- Never assume or default to any size - if not specified, it must be '?'.
- When customer changes size by saying something like 'make it large', only modify the last item mentioned.


3. TOPPING HANDLING:
- Use '?' only for items whose topping isn't specified by customer.
- Use '!' only when customer requests an unavailable topping for an item that exists in menu.
- Use 'No Topping Option' only for items that have no topping option in the menu.
- Never assume or default to any topping - if not specified, it must be '?'.
- Separate multiple toppings for the same item with a slash ('/').
- When the customer changes a topping, update the most recently mentioned item.


4. ORDER MANAGEMENT:
- Clear the order on 'clear everything', 'get rid of everything', or 'cancel all.'
- Replace the entire order when customer says 'scratch that, just X.'


5. ANSWERING QUESTIONS:
-If the customer asks a question about the menu, answer it concisely and do not directly add that item to the order
-If the customer mentions an addition to **those**, answer with the phrase: "what item are you referencing when you say: **input customer response here** ?"
-If the customer asks for something that does not align with the menu, answer with either the phrase: "Sorry, not available" or "Sorry, not in menu" -- Never use the same response twice in a row.

6. OUTPUT FORMAT:
Your response must be a JSON object with these exact keys:
- order_details: String containing the formatted order
- sizes: String of all sizes used
- toppings: String of all toppings used
- answer: String of answer to a customer's question about the menu

7. SPECIAL CASES:
If the customer just says the item by itself, do not clear the order and write down that item. Just append that item to the current order
If the customer just says the toppings by itself without food-items, append the toppings to the right-most item in the context
If the customer orders an item and asks a question about another food item in the menu in the same sentence, do not append the quesitoned item
If the customer orders n amount of an item and then changes the order, separate the items, sizes, and toppings accordingly

Format rules:
- Items: 'n x Item Name'
- Sizes: 'n x Size' or 'n x One Size Option' or 'n x ?' or 'n x !'
- Toppings: 'n x Topping' or 'n x No Topping Option' or 'n x ?' or 'n x !'
- Mixed sizes/toppings: separate with commas
- Multiple toppings: separate with slash ('/')

Note: Never put toppings or sizes in Items, and vice versa
Note: If there are n separate items in order_details, there should also be n separate sizes and n separate toppings


"""
#If the *answer* string includes **what item are you referencing**, extract customer input from *answer* string and adjust **previous output** but replace **those** with current **customer input**


async def process_order(transcription: str, previous_output: str) -> dict:
    """Process an order using OpenAI API"""
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"""
Previous order state: {previous_output}
Menu: {menu_string}
Customer order: {transcription}


Process this order according to the rules and return a JSON response."""}
        ]

        response = await client.chat.completions.create(
            model="gpt-4o",  # or your preferred model
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"}
        )


        # Extract and parse the JSON response
        result = json.loads(response.choices[0].message.content)
        return result


    except Exception as e:
        logger.error(f"Error processing order with OpenAI: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process order: {str(e)}"
        )


# Keep the database helper functions unchanged
async def get_conversation_or_404(id: int, session: AsyncSession) -> Conversation:
    conversation = await session.get(Conversation, id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation not found: {id}"
        )
    return conversation


async def generate_unique_conversation_id(session: AsyncSession) -> str:


    max_attempts = 100  # Prevent infinite loops
    attempt = 0
   
    while attempt < max_attempts:
        # Generate random word
        random_id = RandomWord().word()
       
        # Check for profanity
        if profanity.contains_profanity(random_id):
            attempt += 1
            continue
           
        # Check if ID exists in database
        result = await session.execute(
            select(Conversation).where(Conversation.conversation_id.like(f"{random_id}_%"))
        )
       
        if not result.scalars().first():
            return random_id
           
        attempt += 1
       
    raise RuntimeError("Failed to generate unique profanity-free ID after maximum attempts")


async def get_latest_order_context(session: AsyncSession, base_id: str) -> str:
    result = await session.execute(
        select(Conversation.context)
        .where(Conversation.conversation_id.like(f"{base_id}_%"))
        .order_by(nulls_last(Conversation.timestamp.desc()))
        .limit(1)
    )
    context = result.scalar()
    return context if context else " "


async def get_conversation_version(session: AsyncSession, base_id: str) -> int:
    try:
        result = await session.execute(
            select(func.max(
                func.cast(
                    func.regexp_replace(
                        Conversation.conversation_id,
                        f'^{base_id}_',
                        ''
                    ),
                    type_=Integer
                )
            )).where(
                Conversation.conversation_id.like(f"{base_id}_%")
            )
        )
        latest_version = result.scalar()
        return 0 if latest_version is None else latest_version + 1
    except Exception as e:
        logger.error(f"Error getting conversation version: {str(e)}")
        result = await session.execute(
            select(func.count()).where(
                Conversation.conversation_id.like(f"{base_id}_%")
            )
        )
        count = result.scalar()
        return count


async def get_latest_conversation_id(session: AsyncSession) -> Optional[str]:
    try:
        result = await session.execute(
            select(Conversation.conversation_id)
            .order_by(
                nulls_last(Conversation.timestamp.desc()),
                Conversation.conversation_id.desc()
            )
            .limit(1)
        )
        return result.scalar()
    except Exception as e:
        logger.error(f"Error getting latest conversation ID: {str(e)}")
        return None


@conversation_router.post(
    "/create_and_update",
    status_code=status.HTTP_201_CREATED
)
async def parse_request(
    request_body: RequestBody,
    session: AsyncSession = Depends(get_db)
):
    """Process a customer order and store it in the Conversation table"""
    transcription = request_body.text.strip()


    try:
        # Handle 'done' case
        if "done" in transcription.lower():
            before_done = transcription.lower().split('done')[0].strip()
           
            if before_done:
                latest_conv_id = await get_latest_conversation_id(session)
                if latest_conv_id:
                    base_id = latest_conv_id.split('_')[0]
                    latest_context = await get_latest_order_context(session, base_id)
                    version = await get_conversation_version(session, base_id)


                    crew_result = await process_order(before_done, latest_context)
                    #filtered_crew_result = {k: v for k, v in crew_result.items() if k != 'answer'}
                    final_conversation = Conversation(
                        chunk=before_done,
                        context=json.dumps(crew_result),
                        conversation_id=f"{base_id}_{version}",
                        timestamp=datetime.now(timezone.utc)
                    )
                    session.add(final_conversation)
                    await session.commit()
           
            new_base_id = await generate_unique_conversation_id(session)
           
            new_conversation = Conversation(
                chunk="New customer session",
                context="",
                conversation_id=f"{new_base_id}_0",
                timestamp=datetime.now(timezone.utc)
            )
            session.add(new_conversation)
            await session.commit()
           
            return {"order_details": "", "sizes": "", "toppings": ""}


        # For non-done cases
        latest_conv_id = await get_latest_conversation_id(session)
       
        if not latest_conv_id:
            base_id = await generate_unique_conversation_id(session)
            version = 0
            latest_context = " "
        else:
            result = await session.execute(
                select(Conversation)
                .where(Conversation.conversation_id == latest_conv_id)
                .limit(1)
            )
            latest_conv = result.scalar()
           
            if latest_conv and latest_conv.chunk == "New customer session":
                base_id = latest_conv_id.split('_')[0]
                version = 1
                latest_context = ""
            else:
                base_id = latest_conv_id.split('_')[0]
                version = await get_conversation_version(session, base_id)
                latest_context = await get_latest_order_context(session, base_id)


        # Process order
        result = await process_order(transcription, latest_context)
        #filtered_result = {k: v for k, v in result.items() if k != 'answer'}


        # Save to database
        new_conversation = Conversation(
            chunk=transcription,
            context=json.dumps(result),
            conversation_id=f"{base_id}_{version}",
            timestamp=datetime.now(timezone.utc)
        )
        session.add(new_conversation)
        await session.commit()


        return result


    except Exception as e:
        await session.rollback()
        logger.error(f"Error processing order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process order: {str(e)}"
        )