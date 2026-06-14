import uuid
import logging
from typing import Any
from src.infrastructure.gateways.schemas import AIRequest
from src.application.ai.middleware import AIMiddleware

logger = logging.getLogger("Gateway")

class UnifiedInputGateway:
    """
    Centralized entry layer that standardizes all external inputs (Telegram, Bale, etc.) 
    before they reach the AIMiddleware.
    Acts strictly as a transport normalization layer. 
    Does not contain any conversation management, state machine, or AI logic.
    """
    def __init__(self, ai_middleware: AIMiddleware):
        self.ai = ai_middleware

    def route_request(self, request: AIRequest) -> Any:
        """
        Receives an AIRequest from any external bot adapter, logs the trace, 
        and passes the normalized request to AIMiddleware.
        """
        trace_id = str(uuid.uuid4())
        
        logger.info(
            f"[Gateway] TraceID: {trace_id} | Source: {request.source} | "
            f"ChatID: {request.chat_id} | Payload: {request.payload}"
        )
        
        try:
            # Delegate all actual business logic (including user mapping and conversation management)
            # to the AIMiddleware layer.
            response = self.ai.handle_gateway_request(request)
            
            logger.info(f"[Gateway] TraceID: {trace_id} | Success")
            return response
            
        except Exception as e:
            logger.error(f"[Gateway] TraceID: {trace_id} | Error: {str(e)}")
            raise e
