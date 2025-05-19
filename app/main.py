from langchain_core.messages import HumanMessage
from app.src.graph import build_graph
from app.src.state import save_state
from fastapi import FastAPI, Body
from mangum import Mangum
import logging
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = FastAPI()
handler = Mangum(app)

@app.get("/")
async def root() -> str:
    return "Hello, world!"


@app.post("/")
async def process_input(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    try:
        logger.info(f"Received input: {payload}")
        
        # Extract input from payload
        user_input = payload.get("input", "")
        
        # Process the input (example usage of HumanMessage and build_graph)
        graph = build_graph(model='ollama', temperature=0.0)
        state = graph.invoke({"query": [HumanMessage(content=user_input)]})
        save_state(state)
        
        return {
            "status": "success",
            "result": state["query"][-1].content
        }
    except Exception as e:
        logger.error(f"Error processing input: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }