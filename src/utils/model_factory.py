"""
Simple model factory for automatic model selection based on environment variables.
"""
import os
from dotenv import load_dotenv
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini

# Load environment variables
load_dotenv()

def get_model(temperature=0.3):
    """
    Get appropriate model based on available API keys.

    Priority:
    1. If OPENAI_API_KEY exists -> OpenAIChat
    2. If GOOGLE_API_KEY exists -> Gemini
    3. Default to Gemini if both exist

    Args:
        temperature (float): Model temperature setting

    Returns:
        Model instance (OpenAIChat or Gemini)
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    if openai_key:
        return OpenAIChat(id="gpt-4o-mini", temperature=temperature)
    elif google_key:
        return Gemini(id="gemini-2.5-flash", temperature=temperature)
    else:
        # Fallback to Gemini (most common in current codebase)
        return Gemini(id="gemini-2.5-flash", temperature=temperature)