import os
from fastapi import APIRouter, Depends
# from crewai import Agent, Task, Crew
from pydantic import BaseModel, Field
import pandas as pd
import json
from app.voice_agent_app.models import RequestBody, OrderProcessing
from app.settings import OPENAI_KEY
from openai import OpenAI
from app.voice_agent_app.schemas import OrderProcessingSchema
from app.utils.db_base import get_db
from sqlalchemy.ext.asyncio import AsyncSession


os.environ["OPENAI_API_KEY"] = ""


va_router = APIRouter()

existing_result = ""  # Stores the current state of the processed order
# Menu given as string to agent instead of giving it a csvtool because this method is faster
menu_path = os.path.join(os.path.dirname(__file__), 'menu.csv')

df = pd.read_csv(menu_path)

# Transform to dict structure
menu_string = df.set_index("Item").apply(
    lambda row: {"sizes": row["Size Options"].split(","), "toppings": row["Topping Options"].split(",")}, axis=1
).to_dict()

# Order model with added descriptions and examples
class OrderOutput(BaseModel):
    order_details: str = Field(
        ...,
        description="Comma-separated list of items with quantities",
        example="1 x *item A in menu*, 1 x *item B in menu*, 1 x *item C in menu*"
    )
    sizes: str = Field(
        ...,
        description="Corresponding sizes for each item in order_details",
        example="sizes: 1 x One Size Option, 1 x Small, 1 x Large, 1 x Medium, 1 x ?, 1 x !"
    )
    toppings: str = Field(
        ...,
        description="Corresponding toppings for each item in order_details",
        example="sizes:  1 x No Topping Option, 1 x *Topping X in menu*, 1 x ?, 1 x !"
    )

# Initialize global result for dynamic updates
existing_result = ""

# Agent processing -- Moved this out of for-loop
# I was initializing the same agent several time, impacting its memory
# order_taker_agent = Agent(
#     role="Highly Skilled Waiter",
#     goal="Process the customer order: **{customer_order}** by noting down food items in your notebook: **{previous_output}** that align with **{menu}** and the formatting rules",
#     backstory=(
#         "You're an excellent waiter who has been processing customer orders based on these rules for 48 years!\n" 
#         "\n"
#         "1. MENU VALIDATION:\n"
#         "- ONLY accept items that align with **{menu}**.\n"
#         "- Ignore items that do not align with given menu.\n\n"
#         "\n"
#         "2. SIZE HANDLING:\n"
#         "- Use '?' only for items whose size isn't specified by customer.\n"
#         "- Use '!' only when customer requests an unavailable size for an item that exists in menu.\n"
#         "- Use 'One Size Option' only for items that have exactly one size option in the menu.\n"
#         "- Never assume or default to any size - if not specified, it must be '?'.\n"
#         "- When customer changes size by saying something like 'make it large', only modify the last item mentioned.\n\n"
#         "\n"
#         "3. TOPPING HANDLING:\n"
#         "- Use '?' only for items whose topping isn't specified by customer.\n"
#         "- Use '!' only when customer requests an unavailable topping for an item that exists in menu.\n"
#         "- Use 'No Topping Option' only for items that have no topping option in the menu.\n"
#         "- Never assume or default to any topping - if not specified, it must be '?'.\n"
#         "- Separate multiple toppings for the same item with a slash ('/').\n"
#         "- When the customer changes a topping (e.g., 'actually, no ketchup'), update the most recently mentioned item.\n\n"
#         "\n"
#         "4. ORDER MANAGEMENT:\n"
#         "- Clear the order on 'clear everything', 'get rid of everything', or 'cancel all.'\n"
#         "- Replace the entire order when customer says 'scratch that, just X.'\n"
#         "\n"
#         "\n"
#         "5. OUTPUT FORMAT:\n"
#         "- Items: '1 x Item Name'\n"
#         "- Sizes: '1 x Size' or '1 x One Size Option' or '1 x ?' or '1 x !'\n"
#         "- Toppings: '1 x Topping' or '1 x No Topping Option' or '1 x ?' or '1 x !'\n"
#         "- Mixed sizes or toppings: separate sizes with commas, separate multiple toppings with a slash ('/').\n"
#         "- Different items: separate details with commas.\n\n"
#         "\n"
#         "Example Expected Outputs: (Note: items with letters represent random foods)\n"
#         "'can i have two *item A in menu with many size and topping options* with *Topping A available for Item A* and *Topping B available for Item A*' → order_details: '1 x *item A*, 1 x *item A*', sizes: '1 x ?, 1 x ?', toppings: '1 x *Topping A* / *Topping B*, 1 x *Topping A* / *Topping B*'\n"
#         "'give me a *item B in menu with one size option and no topping option* and *item C in menu with many size and topping options* with *Topping C available for Item C*' → order_details: '1 x *item B*, 1 x *item C*', sizes: '1 x One Size Option, 1 x ?', toppings: '1 x No Topping Option, 1 x *Topping C*'\n"
#         "'i want a large *item D in menu with many size and topping options* with *Topping D available for Item D* make it small and a *item E in menu with many size and topping options*' → order_details: '1 x *item D*, 1 x *item E*', sizes: '1 x Small, 1 x ?', toppings: '1 x *Topping D*, 1 x ?'\n"
#         "'let me have a *item F in menu with one size option and no topping option* and two *item G in menu with many size options and no topping option*' → order_details: '1 x *item F in menu with one size option*, 1 x *item G*, 1 x *item G*', sizes: '1 x One Size Option, 1 x ?, 1 x ?', toppings: '1 x No topping option, 1 x No topping option, 1 x No topping option'\n"
#         "'give me 3 *item J in menu with many size and topping options* one of them a small with *Topping A available for Item J*, one a medium with *Topping B available for Item J* and the other a large with *Topping C available for Item J*' → order_details: '1 x *item J*, 1 x *item J*, 1 x *item J*', sizes: '1 x Small, 1 x Medium, 1 x Large', toppings: '1 x *Topping A*, 1 x *Topping B*, 1 x *Topping C*'\n"
#     )
# )

# # Task assigned to order_taker_agent
# order_task = Task(
#     description=("Process the customer's order chunk: **{customer_order}** by following the formatting rules and carefully updating the current order: **{previous_output}**"),
#     expected_output="Structured order details with items, sizes, and toppings",
#     human_input=False,
#     output_json=OrderOutput,
#     agent=order_taker_agent
# )

# # Not using memory because this is too latent
# order_crew = Crew(
#     agents=[order_taker_agent],
#     tasks=[order_task],
#     verbose = True,
#     memory=False
# )

# # Modified router endpoint
# @va_router.post("/completion")
# async def parse_request(
#     request_body: RequestBody,
#     session: AsyncSession = Depends(get_db)
# ):
#     global existing_result
#     transcription = request_body.text

#     order_details = {
#         'customer_order': transcription.strip(),
#         'menu': menu_string,
#         'previous_output': existing_result
#     }

#     crew_result = order_crew.kickoff(inputs=order_details)

#     if hasattr(crew_result, 'model_dump'):
#         result_dict = crew_result.model_dump()
#     elif hasattr(crew_result, 'dict'):
#         result_dict = crew_result.dict()
#     else:
#         result_dict = crew_result if isinstance(crew_result, dict) else json.loads(str(crew_result))

#     existing_result = result_dict["json_dict"]
    
#     # Create database record
#     new_order = OrderProcessing(
#         transcription=transcription,
#         order_details=result_dict["json_dict"]["order_details"],
#     )
    
#     session.add(new_order)
#     await session.commit()
#     await session.refresh(new_order)

#     return {
#         "order_details": result_dict["json_dict"]["order_details"],
#         "sizes": result_dict["json_dict"]["sizes"],
#         "toppings": result_dict["json_dict"]["toppings"]
#     }