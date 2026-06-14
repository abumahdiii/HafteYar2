import json
import os
from typing import List, Dict, Any, Tuple
from src.application.ai.llm_provider import BaseLLMProvider
from sqlalchemy.orm import Session
from src.infrastructure.database.models.user import User, UserAccount
from src.infrastructure.database.models.team import TeamMember
from src.infrastructure.database.models.ai import Conversation, ExecutionPlan, ExecutionPlanItem
from src.infrastructure.database.models.bot import TelegramUserSession
from src.infrastructure.gateways.schemas import AIRequest, GatewayResponse, InlineButton
from src.domain.utils.ids import generate_id

# Use Cases and Repositories
from src.application.use_cases.team_management import TeamManagementUseCase
from src.infrastructure.database.repositories.team_repository import TeamRepository
from src.infrastructure.database.repositories.project_repository import ProjectRepository, ListRepository

from src.application.use_cases.task_management import TaskManagementUseCase
from src.infrastructure.database.repositories.task_repository import TaskRepository

from src.application.use_cases.subscription import SubscriptionUseCase
from src.infrastructure.database.repositories.subscription import SQLAlchemySubscriptionRepository

class AIMiddleware:
    def __init__(self, db_session: Session, llm_provider: BaseLLMProvider = None):
        self.db = db_session
        self.provider = llm_provider
        self.team_use_case = TeamManagementUseCase(
            team_repo=TeamRepository(db_session),
            project_repo=ProjectRepository(db_session),
            list_repo=ListRepository(db_session)
        )
        self.task_use_case = TaskManagementUseCase(
            task_repo=TaskRepository(db_session),
            project_repo=ProjectRepository(db_session),
            team_repo=TeamRepository(db_session)
        )
        self.sub_use_case = SubscriptionUseCase(
            subscription_repo=SQLAlchemySubscriptionRepository(db_session)
        )

    def _get_or_create_session(self, chat_id: str) -> TelegramUserSession:
        sess = self.db.query(TelegramUserSession).filter_by(chat_id=chat_id).first()
        if not sess:
            sess = TelegramUserSession(chat_id=chat_id, state="IDLE", state_data={})
            self.db.add(sess)
            self.db.commit()
        return sess

    def _update_session(self, sess: TelegramUserSession, state: str, state_data: dict = None):
        sess.state = state
        if state_data is not None:
            sess.state_data = state_data
        self.db.commit()

    def _get_or_create_conversation(self, request: AIRequest) -> Conversation:
        # Lookup UserAccount
        account = self.db.query(UserAccount).filter_by(
            provider=request.source, 
            provider_id=str(request.chat_id)
        ).first()
        
        if not account:
            # Create user
            user = User(username=request.username or f"{request.source}_{request.chat_id}")
            self.db.add(user)
            self.db.commit()
            
            account = UserAccount(user_id=user.id, provider=request.source, provider_id=str(request.chat_id))
            self.db.add(account)
            self.db.commit()
        else:
            user = account.user

        # Get or create active conversation
        conv = self.db.query(Conversation).filter_by(
            user_id=user.id, 
            channel=request.source
        ).order_by(Conversation.created_at.desc()).first()
        
        if not conv:
            conv = Conversation(id=generate_id("con"), user_id=user.id, channel=request.source)
            self.db.add(conv)
            self.db.commit()
            
        return conv

    def _has_pro_access(self, user_id: str, team_id: str) -> bool:
        if not team_id:
            return False
        tm = self.db.query(TeamMember).filter_by(user_id=user_id, team_id=team_id).first()
        if tm and tm.has_ai_access:
            return True
        return False

    def handle_gateway_request(self, request: AIRequest) -> GatewayResponse:
        """
        Processes standard AIRequests from UnifiedInputGateway.
        Resolves conversation context and executes the core logic using State Machine.
        """
        conv = self._get_or_create_conversation(request)
        sess = self._get_or_create_session(request.chat_id)
        
        text = request.payload.strip()

        # Standard Default Buttons for Telegram
        default_buttons = [
            ["👥 مدیریت تیم‌ها", "📝 مدیریت تسک‌ها"],
            ["⚙️ اشتراک‌ها", "🤖 دستیار هوشمند (Pro)"]
        ]
        
        teams_menu = [
            ["➕ ایجاد تیم جدید", "📋 لیست تیم‌های من"],
            ["🔙 بازگشت به منوی اصلی"]
        ]
        
        tasks_menu = [
            ["➕ ایجاد تسک جدید", "📋 تسک‌های من (پروژه‌ها)"],
            ["🔙 بازگشت به منوی اصلی"]
        ]
        
        subscriptions_menu = [
            ["وضعیت اشتراک", "خرید اشتراک"],
            ["🔙 بازگشت به منوی اصلی"]
        ]

        if text in ["/start", "🔙 بازگشت به منوی اصلی"]:
            self._update_session(sess, "IDLE", {})
            return GatewayResponse(
                text="سلام! به سیستم مدیریت تیم هفته‌یار خوش آمدید. لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
                buttons=default_buttons
            )

        # -- Teams Management Navigation --
        if text == "👥 مدیریت تیم‌ها":
            self._update_session(sess, "IDLE", {})
            return GatewayResponse(text="منوی مدیریت تیم‌ها:", buttons=teams_menu)

        if text == "➕ ایجاد تیم جدید":
            self._update_session(sess, "WAITING_TEAM_NAME", {})
            return GatewayResponse(text="لطفاً نام تیم جدید را وارد کنید:", buttons=[["🔙 بازگشت به منوی اصلی"]])

        if text == "📋 لیست تیم‌های من":
            teams = self.team_use_case.get_user_teams(user_id=conv.user_id)
            if not teams:
                return GatewayResponse(text="شما در هیچ تیمی عضو نیستید.", buttons=teams_menu)
            
            inline_buttons = []
            for t in teams:
                inline_buttons.append([InlineButton(text=t.name, callback_data=f"team_{t.id}")])
            return GatewayResponse(text="لیست تیم‌های شما (برای مشاهده جزئیات کلیک کنید):", inline_buttons=inline_buttons, buttons=teams_menu)

        # -- Tasks Management Navigation --
        if text == "📝 مدیریت تسک‌ها":
            self._update_session(sess, "IDLE", {})
            return GatewayResponse(text="منوی مدیریت تسک‌ها:", buttons=tasks_menu)

        if text == "➕ ایجاد تسک جدید":
            # First, user must pick a project.
            teams = self.team_use_case.get_user_teams(user_id=conv.user_id)
            if not teams:
                return GatewayResponse(text="برای ایجاد تسک، ابتدا باید در یک تیم عضو باشید.", buttons=tasks_menu)
            
            inline_buttons = []
            for t in teams:
                inline_buttons.append([InlineButton(text=f"تیم {t.name}", callback_data=f"selteam_{t.id}")])
            return GatewayResponse(text="ابتدا تیم مورد نظر را انتخاب کنید:", inline_buttons=inline_buttons, buttons=[["🔙 بازگشت به منوی اصلی"]])

        if text == "📋 تسک‌های من (پروژه‌ها)":
            teams = self.team_use_case.get_user_teams(user_id=conv.user_id)
            inline_buttons = []
            for t in teams:
                inline_buttons.append([InlineButton(text=f"تیم {t.name}", callback_data=f"viewteam_{t.id}")])
            return GatewayResponse(text="برای مشاهده تسک‌ها، تیم را انتخاب کنید:", inline_buttons=inline_buttons, buttons=tasks_menu)

        # -- Subscriptions Navigation --
        if text == "⚙️ اشتراک‌ها":
            self._update_session(sess, "IDLE", {})
            return GatewayResponse(text="بخش اشتراک‌ها در حال توسعه است. می‌توانید وضعیت اشتراک تیم‌هایتان را از اینجا مدیریت کنید.", buttons=subscriptions_menu)

        # -- State Machine Handlers --
        if sess.state == "WAITING_TEAM_NAME":
            if not text:
                return GatewayResponse(text="نام تیم نمی‌تواند خالی باشد. مجدداً وارد کنید:")
            
            team = self.team_use_case.create_team(name=text, owner_user_id=conv.user_id)
            self._update_session(sess, "IDLE", {})
            return GatewayResponse(text=f"✅ تیم '{team.name}' با موفقیت ساخته شد.", buttons=teams_menu)
            
        if sess.state == "WAITING_TASK_TITLE":
            if not text:
                return GatewayResponse(text="عنوان تسک نمی‌تواند خالی باشد:")
            
            project_id = sess.state_data.get("project_id")
            # For simplicity, if we don't have a list, just pass None and UseCase should handle it or fail.
            # Real implementation might need a list selection step.
            task = self.task_use_case.create_task(
                title=text,
                project_id=project_id,
                creator_id=conv.user_id,
                list_id=None # Let UseCase generate default if implemented or requires fixing
            )
            self._update_session(sess, "IDLE", {})
            return GatewayResponse(text=f"✅ تسک '{task.title}' ایجاد شد.", buttons=tasks_menu)

        # -- Callbacks --
        if request.is_callback:
            if text.startswith("team_"):
                team_id = text.split("_")[1]
                return GatewayResponse(text=f"جزئیات تیم انتخاب شده (شناسه: {team_id}). قابلیت‌های این بخش در حال توسعه است.", buttons=teams_menu)
            
            if text.startswith("selteam_"):
                team_id = text.split("_")[1]
                self._update_session(sess, "WAITING_TASK_TITLE", {"team_id": team_id, "project_id": f"dummy_proj_for_{team_id}"})
                return GatewayResponse(text="عنوان تسک جدید را وارد کنید:")
            
            return GatewayResponse(text="عملیات ناشناخته", buttons=default_buttons)

        # -- AI Flow --
        if text == "🤖 دستیار هوشمند (Pro)" or not text.startswith("/") and sess.state == "IDLE":
            if self._has_pro_access(conv.user_id, conv.active_team_id):
                if text == "🤖 دستیار هوشمند (Pro)":
                    return GatewayResponse(
                        text="شما دسترسی Pro دارید! منتظر شنیدن درخواست‌های شما هستم.",
                        buttons=default_buttons
                    )
                # Actual AI generation
                plan = self.process_user_input(conversation_id=conv.id, user_input=text)
                return GatewayResponse(
                    text=f"✅ پلان ایجاد شد.\nشناسه: `{plan.id}`\nوضعیت: {plan.status}",
                    buttons=default_buttons
                )
            else:
                return GatewayResponse(
                    text="دسترسی به این بخش نیازمند لایسنس دستیار هوشمند در تیم شماست. لطفاً حساب خود را ارتقاء دهید.",
                    buttons=default_buttons,
                    is_pro_upsell=True
                )
        
        # Fallback
        return GatewayResponse(text="دستور نامعتبر", buttons=default_buttons)

    def process_user_input(self, conversation_id: str, user_input: str) -> ExecutionPlan:
        """
        Minimal orchestration flow:
        1. Load Conversation
        2. Extract context
        3. Inject into prompt
        4. Call Gapgpt
        5. Generate ExecutionPlan (NO EXECUTION)
        """
        # 1. Load Conversation context
        conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        # 2. Extract context snapshot
        context_snapshot = {
            "team_id": conversation.active_team_id,
            "project_id": conversation.active_project_id,
            "member_id": conversation.active_member_id
        }

        # 3. Build System Prompt with Context
        system_prompt = f"""
You are the Haftyar AI Bot, an AI-first team and project management assistant.
Your goal is to parse the user's intent and propose a structured execution plan.

CURRENT ACTIVE CONTEXT:
Team ID: {context_snapshot['team_id'] or 'None'}
Project ID: {context_snapshot['project_id'] or 'None'}
Member ID: {context_snapshot['member_id'] or 'None'}

Return your response strictly as a JSON array of operations (ExecutionPlanItems).
Each operation must have:
- "tool_name": string (e.g. "CreateTask", "GenerateWeeklyReport")
- "parameters": dictionary of tool arguments

Do not execute the actions, just propose the plan.
"""

        # 4. Call Gapgpt API
        # Using structured output or basic JSON mode depending on Gapgpt support
        # For this MVP, we prompt for JSON.
        try:
            raw_response = self.provider.generate_plan(system_prompt=system_prompt, user_input=user_input)
            
            try:
                plan_items_data = json.loads(raw_response)
            except json.JSONDecodeError:
                if "```json" in raw_response:
                    clean_json = raw_response.split("```json")[1].split("```")[0].strip()
                    plan_items_data = json.loads(clean_json)
                else:
                    raise ValueError(f"LLM returned invalid JSON: {raw_response}")

        except Exception as e:
            print(f"LLM call failed: {str(e)}")
            raise e

        # 5. Generate ExecutionPlan
        plan = ExecutionPlan(
            id=generate_id("pln"),
            conversation_id=conversation.id,
            user_id=conversation.user_id,
            team_id=context_snapshot['team_id'],
            project_id=context_snapshot['project_id'],
            member_id=context_snapshot['member_id'],
            context_snapshot=context_snapshot,
            status="PENDING"
        )
        self.db.add(plan)
        
        # Add Items
        for item_data in plan_items_data:
            item = ExecutionPlanItem(
                id=generate_id("itm"),
                plan_id=plan.id,
                tool_name=item_data.get("tool_name", "UnknownTool"),
                parameters=item_data.get("parameters", {}),
                initial_state="GREEN",
                final_state="GREEN",
                current_version_index=1,
                refinement_history=[],
                executed=False
            )
            self.db.add(item)
            
        self.db.commit()
        self.db.refresh(plan)
        
        return plan

    def review_plan(self, plan_id: str, reviews: List[Dict[str, Any]]) -> ExecutionPlan:
        plan = self.db.query(ExecutionPlan).filter(ExecutionPlan.id == plan_id).first()
        if not plan:
            raise ValueError("Plan not found")
        
        for review in reviews:
            item_id = review.get("item_id")
            final_state = review.get("final_state")
            feedback = review.get("feedback_text")
            
            item = next((i for i in plan.items if i.id == item_id), None)
            if item:
                item.final_state = final_state
                # We could store feedback temporarily or just rely on passing it directly to refine
                # but let's store it dynamically in parameters or just use it directly in API layer.
                # Actually, if we want to reprompt later, it's best to process it in `refine_plan`.
                # For now, we just set the final state.
        
        self.db.commit()
        return plan

    def refine_plan(self, plan_id: str, feedbacks: Dict[str, str]) -> Tuple[ExecutionPlan, int]:
        """
        Takes a plan and a dict of item_id -> feedback_text.
        Only items with final_state == 'YELLOW' are processed.
        """
        plan = self.db.query(ExecutionPlan).filter(ExecutionPlan.id == plan_id).first()
        if not plan:
            raise ValueError("Plan not found")
            
        refined_count = 0
        for item in plan.items:
            if item.final_state == "YELLOW" and item.id in feedbacks:
                feedback = feedbacks[item.id]
                # Reprompt LLM
                prompt = f"You previously generated these parameters: {json.dumps(item.parameters)}. The user requested the following change: {feedback}. Return the updated JSON parameters strictly."
                try:
                    raw_response = self.provider.refine_parameters(original_parameters=item.parameters, feedback=feedback)
                    
                    try:
                        new_params = json.loads(raw_response)
                    except json.JSONDecodeError:
                        if "```json" in raw_response:
                            clean_json = raw_response.split("```json")[1].split("```")[0].strip()
                            new_params = json.loads(clean_json)
                        else:
                            raise ValueError(f"LLM returned invalid JSON for refinement: {raw_response}")
                except Exception as e:
                    print(f"LLM call failed for refinement: {str(e)}")
                    raise e
                    
                # Store old version in history
                history = list(item.refinement_history) if item.refinement_history else []
                history.append({
                    "version": item.current_version_index,
                    "content": item.parameters
                })
                
                item.refinement_history = history
                item.parameters = new_params
                item.current_version_index += 1
                item.final_state = "GREEN"
                refined_count += 1
                
        self.db.commit()
        return plan, refined_count
