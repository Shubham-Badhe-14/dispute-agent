import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

def get_llm():
    provider = os.getenv("LLM_PROVIDER", "google_genai")
    model = os.getenv("LLM_MODEL", "gemini-3.6-flash")
    return init_chat_model(model, model_provider=provider)
