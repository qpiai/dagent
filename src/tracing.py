"""Centralized tracing setup for the entire application."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Initialize tracing once for the entire application
try:
    import openlit
    from langfuse import get_client, observe

    # Initialize Langfuse client
    langfuse = get_client()

    # Initialize OpenLIT instrumentation globally
    openlit.init(tracer=langfuse._otel_tracer, disable_batch=True)

    print("Tracing initialized successfully")

except Exception as e:
    print(f"Tracing initialization failed: {e}")
    # Create dummy objects to prevent import errors
    class DummyLangfuse:
        def update_current_trace(self, **kwargs):
            pass

    def observe():
        def decorator(func):
            return func
        return decorator

    langfuse = DummyLangfuse()

# Export for other modules
__all__ = ['langfuse', 'observe']