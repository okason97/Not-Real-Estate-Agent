from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

def init_llm(model='ollama', temperature=0.0):
    if model == 'ollama':
        llm = init_chat_model("ollama:gemma3:12b", temperature=temperature)
    elif model == 'ollama-remote':
        load_dotenv()
        ollama_host = os.environ.get("OLLAMA_HOST")
        llm = init_chat_model("ollama:gemma3:12b", temperature=temperature, base_url=f"http://{ollama_host}")
    elif model == 'openai':
        load_dotenv()
        llm = init_chat_model("openai:o3-mini", temperature=temperature)
    elif model == 'claude':
        load_dotenv()
        llm = init_chat_model("anthropic:claude-3-5-sonnet-latest", temperature=temperature)
    elif model == 'google':
        load_dotenv()
        llm = init_chat_model("google_vertexai:gemini-2.5-flash-preview-04-17", temperature=temperature)
    else:
        raise ValueError(f"Model {model} not supported.")
    return llm