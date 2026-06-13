from typing import Dict, Any, Callable

class ToolRegistry:
    """
    Minimal first version tool registry.
    Maps tool_name to use_case handler.
    """
    def __init__(self):
        self._registry: Dict[str, Callable] = {}

    def register(self, tool_name: str, handler: Callable):
        self._registry[tool_name] = handler

    def get_handler(self, tool_name: str) -> Callable:
        if tool_name not in self._registry:
            raise ValueError(f"Tool {tool_name} is not registered.")
        return self._registry[tool_name]
        
    def get_all_tool_names(self) -> list[str]:
        return list(self._registry.keys())

# Global registry instance
registry = ToolRegistry()
