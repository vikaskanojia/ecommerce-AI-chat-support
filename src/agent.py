"""The LangGraph agent: state, reasoner node, tool node, and thread-based memory."""

from typing import Annotated, TypedDict

import streamlit as st
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

SYSTEM_PROMPT = (
    "You are a helpful ecommerce store assistant. Use the product search/filter tools for "
    "product questions, and the FAQ tool for store policy questions (shipping, returns, "
    "payments, account, etc). Never invent products, prices, brands, or policies that "
    "aren't in the tool results -- if nothing matches, say so clearly."
)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


@st.cache_resource
def build_agent(_tools: list, model_name: str, temperature: float, max_retries: int):
    llm = ChatGroq(model=model_name, temperature=temperature, max_retries=max_retries)
    llm_with_tools = llm.bind_tools(_tools)

    def reasoner(state: AgentState):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    def should_continue(state: AgentState):
        last = state["messages"][-1]
        return "tools" if getattr(last, "tool_calls", None) else END

    graph = StateGraph(AgentState)
    graph.add_node("reasoner", reasoner)
    graph.add_node("tools", ToolNode(_tools))
    graph.set_entry_point("reasoner")
    graph.add_conditional_edges("reasoner", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "reasoner")

    return graph.compile(checkpointer=MemorySaver())
