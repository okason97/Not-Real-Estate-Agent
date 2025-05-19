from langchain_core.messages import HumanMessage
from app.src.graph import build_graph
from fastapi import FastAPI
from mangum import Mangum
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = FastAPI()
handler = Mangum(app)

@app.get("/")
async def root() -> str:
    return "Hello, world!"

'''
graph = build_graph(model='ollama', temperature=0.0)

user_input = input("Enter a message: ")
print(user_input)
state = graph.invoke({"query": [HumanMessage(content=user_input)]})

print(state["query"][-1].content)
'''