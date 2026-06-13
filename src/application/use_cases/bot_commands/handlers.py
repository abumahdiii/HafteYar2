from typing import Dict, Any
from src.application.use_cases.bot_commands.router import bot_router

@bot_router.register("/start")
def handle_start(user_id: str, context: Dict[str, Any]) -> str:
    return "سلام! به ربات هفته‌یار خوش آمدید. برای راهنمایی /help را ارسال کنید."

@bot_router.register("/help")
def handle_help(user_id: str, context: Dict[str, Any]) -> str:
    return (
        "دستورات موجود:\n"
        "/teams - مشاهده تیم‌های شما\n"
        "/create_task [متن] - ایجاد تسک جدید در پروژه عمومی"
    )

@bot_router.register("/teams")
def handle_teams(user_id: str, context: Dict[str, Any]) -> str:
    team_repo = context.get("team_repo")
    if not team_repo:
        return "خطای سیستم."
        
    teams = team_repo.get_all_for_user(user_id)
    if not teams:
        return "شما در هیچ تیمی عضو نیستید."
        
    lines = ["تیم‌های شما:"]
    for t in teams:
        lines.append(f"- {t.name}")
    return "\n".join(lines)

@bot_router.set_default
def handle_default(user_id: str, context: Dict[str, Any]) -> str:
    return "دستور نامعتبر است. لطفاً /help را ارسال کنید."
