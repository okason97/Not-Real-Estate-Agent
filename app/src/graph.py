from langgraph.graph import StateGraph, START, END
from app.src.state import AgentState
from app.src.nodes import LLM, scrape_node

def build_graph(model='ollama', temperature=0.0):

    graph_builder = StateGraph(AgentState)

    llm = LLM(model=model, temperature=temperature)

    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever
    # the node is used.
    graph_builder.add_node("url_agent", llm.url_agent)
    graph_builder.add_node("scrape_node", scrape_node)
    graph_builder.add_node("analize_agent", llm.analize_agent)
    graph_builder.add_node("recomend_agent", llm.recomend_agent)

    graph_builder.add_edge(START, "url_agent")
    graph_builder.add_edge("url_agent", "scrape_node")
    graph_builder.add_edge("scrape_node", "analize_agent")
    graph_builder.add_edge("analize_agent", "recomend_agent")
    graph_builder.add_edge("recomend_agent", END)

    return graph_builder.compile()

def build_url_graph(model='ollama', temperature=0.0):

    graph_builder = StateGraph(AgentState)

    llm = LLM(model=model, temperature=temperature)

    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever
    # the node is used.
    graph_builder.add_node("url_agent", llm.url_agent)

    graph_builder.add_edge(START, "url_agent")
    graph_builder.add_edge("url_agent", END)

    return graph_builder.compile()

def build_scrape_graph(model='ollama', temperature=0.0):

    graph_builder = StateGraph(AgentState)

    llm = LLM(model=model, temperature=temperature)

    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever
    # the node is used.
    graph_builder.add_node("url_agent", llm.url_agent)
    graph_builder.add_node("scrape_node", scrape_node)

    graph_builder.add_edge(START, "url_agent")
    graph_builder.add_edge("url_agent", "scrape_node")
    graph_builder.add_edge("scrape_node", END)

    return graph_builder.compile()


def build_scrape_graphv2(model='ollama', temperature=0.0):

    graph_builder = StateGraph(AgentState)

    llm = LLM(model=model, temperature=temperature)

    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever
    # the node is used.
    graph_builder.add_node("query_data_agent", llm.query_data_agent)
    graph_builder.add_node("scrape_node", scrape_node)

    graph_builder.add_edge(START, "query_data_agent")
    graph_builder.add_edge("query_data_agent", "scrape_node")
    graph_builder.add_edge("scrape_node", END)

    return graph_builder.compile()

def build_analize_graph(model='ollama', temperature=0.0):

    graph_builder = StateGraph(AgentState)

    llm = LLM(model=model, temperature=temperature)

    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever
    # the node is used.
    graph_builder.add_node("url_agent", llm.url_agent)
    graph_builder.add_node("scrape_node", scrape_node)
    graph_builder.add_node("analize_agent", llm.analize_agent)

    graph_builder.add_edge(START, "url_agent")
    graph_builder.add_edge("url_agent", "scrape_node")
    graph_builder.add_edge("scrape_node", "analize_agent")
    graph_builder.add_edge("analize_agent", END)

    return graph_builder.compile()