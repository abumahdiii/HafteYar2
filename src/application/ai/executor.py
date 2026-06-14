import json
import re
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from src.infrastructure.database.models.ai import ExecutionPlan, ExecutionPlanItem
from src.application.ai.tool_registry import registry
from src.domain.exceptions import InvalidOperationError

class PlanExecutor:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def resolve_dependencies(self, parameters: Dict[str, Any], resolved_vars: Dict[str, str]) -> Dict[str, Any]:
        """
        Replaces variables like ${ref_project_id.id} with their actual resolved values.
        """
        params_str = json.dumps(parameters)
        
        # Regex to find patterns like ${var_name.id}
        pattern = r"\$\{([^}]+)\.id\}"
        
        def replacer(match):
            var_name = match.group(1)
            if var_name in resolved_vars:
                return resolved_vars[var_name]
            raise InvalidOperationError(f"Unresolved dependency: {var_name}")
            
        resolved_str = re.sub(pattern, replacer, params_str)
        return json.loads(resolved_str)

    def execute_plan(self, plan_id: str) -> ExecutionPlan:
        plan = self.db_session.query(ExecutionPlan).filter(ExecutionPlan.id == plan_id).first()
        if not plan:
            raise InvalidOperationError("Plan not found")
            
        if any(item.final_state == "YELLOW" for item in plan.items):
            raise InvalidOperationError("Cannot execute plan containing YELLOW items. Please review or refine them first.")

        # Aggregate variables for dependency resolution
        resolved_vars: Dict[str, str] = {}
        
        # Sort items by some order if needed, but since we rely on sequential list index, we execute as is
        # Actually, let's just execute them in the order they appear.
        
        failed_any = False
        executed_any = False
        
        for item in plan.items:
            if item.final_state == "RED":
                continue # Skip rejected items
                
            if item.executed:
                continue # Already executed
                
            try:
                # 1. Resolve Dependencies
                resolved_params = self.resolve_dependencies(item.parameters, resolved_vars)
                
                # 2. Add Context Snapshot data (team_id, project_id, member_id, user_id)
                # The UseCase might need current_user_id or team_id.
                context = plan.context_snapshot or {}
                
                # 3. Get Tool Handler
                handler = registry.get_handler(item.tool_name)
                
                # 4. Execute
                result = handler(db_session=self.db_session, context=context, params=resolved_params)
                
                # 5. Extract newly created IDs if the item declared a reference ID
                # (e.g., if item had project_reference_id="ref_xyz", and result has id="prj_123")
                declared_ref = item.parameters.get("project_reference_id") or item.parameters.get("reference_id")
                if declared_ref and result and hasattr(result, "id"):
                    resolved_vars[declared_ref] = result.id
                    
                # Mark as executed
                item.executed = True
                self.db_session.commit()
                executed_any = True
                
            except Exception as e:
                # Fail fast on the first error to avoid cascading corruptions
                failed_any = True
                # Could log the error to the item here
                break
                
        # Recalculate Aggregate Status
        self._update_plan_status(plan)
        return plan

    def _update_plan_status(self, plan: ExecutionPlan):
        all_executed = all(item.executed for item in plan.items if item.final_state != "RED")
        all_rejected = all(item.final_state == "RED" for item in plan.items)
        any_executed = any(item.executed for item in plan.items)
        any_failed_or_rejected = any(not item.executed for item in plan.items)
        
        if all_rejected:
            plan.status = "REJECTED"
        elif all_executed and len(plan.items) > 0:
            plan.status = "EXECUTED"
        elif any_executed and any_failed_or_rejected:
            plan.status = "PARTIALLY_EXECUTED"
        else:
            plan.status = "FAILED"
            
        self.db_session.commit()
