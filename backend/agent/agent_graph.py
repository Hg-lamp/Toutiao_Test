
from operator import add
from typing import TypedDict, Literal, Annotated

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langgraph.constants import END, START
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from loguru import logger

from backend.config.model import chat_model, tool_model, structured_react_model, structured_intent_model
from backend.config.prompt_template import INTENT_MESSAGES, OVER_ALL_PROMPT
from backend.services.Rag import Rag
# from backend.services.tool_worker import ToolWorker
from backend.services.tools import TOOLS
from backend.utils.toolnode_cache_func import wrap_tool_call


#图状态定义
class OverAllState(MessagesState):
    input:str
    output:str
    intent:str
    context:list[str]
    retry_count:Annotated[int,add]


class OutputState(TypedDict):
    output:str

#节点定义

#意图识别
async def intent_node(state:OverAllState)->OverAllState:
    msg =INTENT_MESSAGES+[HumanMessage(state["input"])]
    intent_msg = await structured_intent_model.ainvoke(msg)
    return {
        "intent":intent_msg.data,
        "messages":AIMessage(content=f"判断到用户意图，执行策略：{intent_msg.data}")
    }

async def intent_choose_router(state:OverAllState)->Command[Literal["rag_node","tool_node","llm_node"]]:
    if state["intent"]=="rag":
        return Command(goto="rag_node")
    elif "tool" in state["intent"]:
        return Command(
            update={
                "messages":await tool_model.ainvoke([SystemMessage(content="根据用户的问题使用工具进行回答"),HumanMessage(content=state["input"])])
            },
            goto="tool_node")
    return Command(goto="llm_node")


async def rag_node(state:OverAllState)->OverAllState:
    rag_msg=[SystemMessage("请你对用户问题进行提炼总结，返回问题的关键词，以方便下一步作为检索关键词进行数据检索"),HumanMessage(content=state['input'])]
    core_content = (await chat_model.ainvoke(rag_msg)).content
    context = await Rag(core_content).run()
    return {
        "context":context,
        "messages":SystemMessage(content=f"知识库检索结果如下：\n{context}\n请基于以上信息回答用户的问题")
    }


async def llm_node(state:OverAllState)->OverAllState:
    ult_res = await chat_model.ainvoke(state["messages"])
    # 清理reasoning_content
    # ult_res.additional_kwargs.pop("reasoning_content", None)
    return {
        "messages":ult_res
    }



async def react_node(state:OverAllState)->Command[Literal["intent_node","__end__"]]:
    if state["retry_count"]>=3:
        # 超过重试次数，直接使用最后一条消息作为输出
        return Command(update={
            "output":state["messages"][-1].content if state["messages"] else "抱歉，无法回答该问题",
        },goto=END)
    react_msg=state["messages"]+[SystemMessage(content="请你对从最新一个用户问题到得到最后答案的这一系列会话，进行判断，判断是否解决了用户的问题。只回答一个词：解决了就返回True，没有就返回False")]
    res = await structured_react_model.ainvoke(react_msg)
    # 清理推理模型返回的reasoning_content
    # res.additional_kwargs.pop("reasoning_content", None)
    # content = res.content.strip()
    if res.is_solved:
        return Command(update={
            "output":state["messages"][-1].content,
        },goto=END)
    else:
        return Command(update={"retry_count":1},goto='intent_node')



async def final_logger(state:OverAllState)->OverAllState:
    logger.info(f"输入内容：{state['input']},意图识别为：{state['intent']},回溯次数：{state['retry_count']}")
    return {}


builder = StateGraph(state_schema=OverAllState,output_schema=OutputState)
builder.add_node("llm_node",llm_node)
builder.add_node("rag_node",rag_node)
builder.add_node("tool_node",ToolNode(tools=TOOLS,awrap_tool_call=wrap_tool_call))#)
builder.add_node("react_node",react_node)
builder.add_node("intent_choose_router",intent_choose_router)
builder.add_node("intent_node",intent_node)
builder.add_node("final_logger",final_logger,defer=True)#延迟节点，对整个图的执行进行一次总结

builder.add_edge(START,"intent_node")
builder.add_edge("intent_node","intent_choose_router")
builder.add_edge("tool_node","llm_node")
builder.add_edge("rag_node","llm_node")
builder.add_edge("llm_node","react_node")

graph= builder.compile()

async def ai_response(user_question:str,user_chat_all:list[BaseMessage]):
    ult_msg=[SystemMessage(content=OVER_ALL_PROMPT)]+user_chat_all
    res = await graph.ainvoke({"messages":ult_msg,"input":user_question,"retry_count":0})
    return res["output"]