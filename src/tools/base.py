"""Base classes and interfaces for Agno tools."""

from agno.tools import Toolkit
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


class BaseAgnoTool(Toolkit):
    """Base class for custom Agno tools."""
    
    def __init__(self, name: str, tools: List, **kwargs):
        """Initialize the toolkit with name and tools."""
        super().__init__(name=name, tools=tools, **kwargs)
        logger.info(f"Initialized {name} toolkit")
    
    def _log_tool_call(self, tool_name: str, args: Dict[str, Any]) -> None:
        """Log tool calls for debugging."""
        logger.info(f"Calling {tool_name} with args: {args}")
    
    def _handle_error(self, tool_name: str, error: Exception) -> str:
        """Handle tool execution errors."""
        error_msg = f"Error in {tool_name}: {str(error)}"
        logger.error(error_msg)
        return error_msg