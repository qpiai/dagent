"""Centralized tracing setup for the entire application."""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Reduce OpenLIT logging verbosity
logging.getLogger("openlit").setLevel(logging.WARNING)
logging.getLogger("opentelemetry").setLevel(logging.WARNING)

# Initialize tracing once for the entire application
try:
    # import openlit  # Temporarily disabled for cleaner output
    from langfuse import get_client, observe

    # Initialize Langfuse client
    langfuse = get_client()

    #Initialize OpenLIT instrumentation globally with console output disabled
    # openlit.init(
    #     tracer=langfuse._otel_tracer,
    #     disable_batch=True,
    #     collect_gpu_stats=False,
    #     otlp_endpoint=None  # Disable OTLP export to avoid connection errors
    # )

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