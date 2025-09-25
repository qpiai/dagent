"""Tools package for Agno agents."""

from .yfinance_tools import YFinanceTools
from .web_search import WebSearchTools
from .file_editor import FileEditorTools
from .base import BaseAgnoTool
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

__all__ = [
    'YFinanceTools',
    'WebSearchTools',
    'FileEditorTools',
    'BaseAgnoTool'
]

# Tool registry for easy access
AVAILABLE_TOOLS = {
    'YFinanceTools': YFinanceTools,
    'WebSearch': WebSearchTools,
    'FileEditor': FileEditorTools
}

def get_tool_by_name(tool_name: str):
    """Get a tool class by name."""
    return AVAILABLE_TOOLS.get(tool_name)

def list_available_tools():
    """List all available tool names."""
    return list(AVAILABLE_TOOLS.keys())