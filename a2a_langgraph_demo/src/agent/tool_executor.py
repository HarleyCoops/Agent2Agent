"""
Tool executor for LangGraph agent.
"""

from typing import Dict, List, Any, Optional, Union, Callable


class ToolExecutor:
    """A simple tool executor for LangGraph agent."""

    def __init__(self, tools: List[Callable]):
        """Initialize the tool executor with a list of tools."""
        self.tools = tools
        self.tool_map = {}

        for tool in tools:
            # Handle both regular functions and StructuredTool objects
            if hasattr(tool, 'name'):
                self.tool_map[tool.name] = tool
            elif hasattr(tool, '__name__'):
                self.tool_map[tool.__name__] = tool
            else:
                raise ValueError(f"Tool {tool} does not have a name attribute or __name__ attribute")

    def invoke(self, input_data: Dict[str, Any]) -> Any:
        """
        Invoke a tool with the given input data.

        Args:
            input_data: A dictionary with the tool name and parameters.
                Example: {"tool_name": "currency_conversion", "amount": 100, "from_currency": "USD", "to_currency": "EUR"}

        Returns:
            The result of the tool execution.
        """
        tool_name = input_data.pop("tool_name")

        if tool_name not in self.tool_map:
            raise ValueError(f"Tool {tool_name} not found. Available tools: {list(self.tool_map.keys())}")

        tool = self.tool_map[tool_name]
        return tool(**input_data)
