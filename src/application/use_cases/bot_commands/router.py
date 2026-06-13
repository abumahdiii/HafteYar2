from typing import Callable, Dict, Any, Optional

CommandHandler = Callable[[str, Dict[str, Any]], Optional[str]]

class CommandRouter:
    def __init__(self):
        self._handlers: Dict[str, CommandHandler] = {}
        self._default_handler: Optional[CommandHandler] = None

    def register(self, command_name: str):
        def decorator(func: CommandHandler):
            self._handlers[command_name] = func
            return func
        return decorator

    def set_default(self, func: CommandHandler):
        self._default_handler = func
        return func

    def route(self, command: str, user_id: str, context: Dict[str, Any]) -> str:
        """Routes the command and returns the response message."""
        # Simple extraction: First word is the command
        parts = command.strip().split(" ", 1)
        base_cmd = parts[0].lower()
        args_text = parts[1] if len(parts) > 1 else ""
        
        context["args_text"] = args_text

        if base_cmd in self._handlers:
            handler = self._handlers[base_cmd]
            response = handler(user_id, context)
            if response:
                return response
                
        if self._default_handler:
            return self._default_handler(user_id, context) or "Command not recognized."
            
        return "Unknown command."

# Global instance for the application
bot_router = CommandRouter()
