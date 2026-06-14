import secrets
import string

def generate_id(prefix: str, length: int = 24) -> str:
    """Generate a random URL-safe ID with a given prefix."""
    # Ensure URL safe characters
    alphabet = string.ascii_letters + string.digits
    random_str = ''.join(secrets.choice(alphabet) for _ in range(length))
    return f"{prefix}_{random_str}"

def new_user_id() -> str: return generate_id("usr")
def new_account_id() -> str: return generate_id("acc")
def new_team_id() -> str: return generate_id("tm")
def new_member_id() -> str: return generate_id("mbr")
def new_project_id() -> str: return generate_id("prj")
def new_list_id() -> str: return generate_id("lst")
def new_task_id() -> str: return generate_id("tsk")
def new_assignee_id() -> str: return generate_id("asn")
def new_comment_id() -> str: return generate_id("cmt")
def new_provider_id() -> str: return generate_id("prv")
def new_model_id() -> str: return generate_id("mdl")
def new_usage_log_id() -> str: return generate_id("usg")
