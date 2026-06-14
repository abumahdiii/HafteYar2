import json
import os
from typing import List, Dict, Any, Tuple
from src.application.ai.llm_provider import BaseLLMProvider
from sqlalchemy.orm import Session
from src.infrastructure.database.models.ai import Conversation, ExecutionPlan, ExecutionPlanItem
from src.domain.utils.ids import generate_id

class AIMiddleware:
    def __init__(self, db_session: Session, llm_provider: BaseLLMProvider = None):
        self.db = db_session
        self.provider = llm_provider

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
