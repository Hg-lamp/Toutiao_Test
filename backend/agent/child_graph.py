from typing import Literal

from langchain_core.messages import HumanMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command

from backend.config.graph_config import retry_policy
from backend.services.tools import CHILD_TOOLS


class ChildState(MessagesState):
    input:str
    output:str

class InputState(MessagesState):
    input:str

class OutputState(MessagesState):
    output:str

async def llm_node(child_state: ChildState)->ChildState:
    from backend.config.model import child_model
    history_chat = child_state['messages']
    res =await child_model.ainvoke(history_chat)
    return {
        "messages":[res]
    }

async def router(state:ChildState)->Command[Literal["__end__","tool_node"]]:
    if state["messages"][-1].tool_calls:
        return Command(goto="tool_node")
    output = state["messages"][-1].content

    return Command(goto="__end__",
            update={
                "output":output
            })


builder= StateGraph(state_schema=ChildState,input_schema=InputState,output_schema=OutputState)

builder.add_node('llm_node',llm_node,timeout=60,retry_policy=retry_policy)
builder.add_node('tool_node',ToolNode(tools=CHILD_TOOLS),timeout=60,retry_policy=retry_policy)
builder.add_node("router",router)

builder.add_edge(START,"llm_node")
builder.add_edge("llm_node","router")
builder.add_edge("tool_node","llm_node")

child_graph=builder.compile()

async def child_output(task:str):
    res =await child_graph.ainvoke({"input":task,"messages":[HumanMessage(content=task)]},config={
        "callbacks":None
    })
    return res["output"]
