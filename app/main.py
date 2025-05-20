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

@app.post("/")
async def process_input(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    try:
        logger.info(f"Received input: {payload}")
        
        # Extract input from payload
        user_input = payload.get("prompt", "")
        #user_input = "quiero un depto en la plata para una persona moderno con cochera"

        # Process the input (example usage of HumanMessage and build_graph)
        logger.info("Attempting to build graph...")
        try:
            graph = build_graph(model='ollama-remote', temperature=0.0)
            logger.info("Graph built successfully")
        except Exception as e:
            logger.error(f"Error building graph: {str(e)}")
            raise

        logger.info("Invoking graph...")
        state = graph.invoke({"query": [HumanMessage(content=user_input)]})
        logger.info("Graph invoked successfully")

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