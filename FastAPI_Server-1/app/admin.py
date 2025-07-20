from starlette_admin.contrib.sqla import Admin, ModelView
from .settings import async_engine
from .users_app.models import *
from .conversations_app.models import Conversation

# Create the admin panel
admin = Admin(engine=async_engine, title="Voiceagent Admin")

class UserModelAdmin(ModelView):
    label = "Users"
    icon = "fa fa-user"
    fields = ["id", "username", "email", "full_name", "is_admin", "is_verified"]
    searchable_fields = ["username", "email", "full_name"]
    list_display = ["id", "username", "email", "is_admin"]

admin.add_view(UserModelAdmin(UserModel))

class ConversationModelAdmin(ModelView):
    label = "Conversations"
    icon = "fa fa-comments"
    fields = [
        "id",
        "conversation_id",
        "timestamp",
        "chunk",
        "context",
        "inferred_command",
        "ideal_inference",
        "initial_review_by",
        "final_review_by",
    ]
    searchable_fields = ["conversation_id", "chunk", "context"]
    list_display = [
        "id",
        "conversation_id",
        "timestamp",
        "initial_review_by",
        "final_review_by",
    ]
    form_args = {
        "initial_review_by": {"label": "Initial Reviewer"},
        "final_review_by": {"label": "Final Reviewer"},
    }

admin.add_view(ConversationModelAdmin(Conversation))

