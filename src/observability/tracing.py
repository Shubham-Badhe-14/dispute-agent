import os
from langfuse.langchain import CallbackHandler
from langfuse import observe

def get_langfuse_handler():
    """
    Returns the Langfuse CallbackHandler for v3 SDK.
    It automatically picks up LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, 
    and LANGFUSE_HOST from the environment variables.
    """
    # Initialize without explicit credentials to rely on env vars (v3 approach)
    handler = CallbackHandler()
    return handler
