from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Command
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from backend.config.graph_config import retry_policy
from backend.config.model import tool_model
from backend.config.db_config import CHECKPOINTER_DATABASE_URL
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.errors import GraphRecursionError
from backend.config.prompt_template import OVER_ALL_PROMPT
from backend.services.tools import PARENT_TOOLS
from loguru import logger

class ParentState(MessagesState):
    input : str
    output:str

class input_state(MessagesState):
    input:str

class output_state(MessagesState):
    output:str


class private_state(MessagesState):
    pass
async def llm_node(parent_state: ParentState)->ParentState:
    history_msg = list(parent_state['messages'])

    # 系统提示词不写入 checkpoint，每次调用时确保置于消息首位，
    # 避免历史消息被持久化后再次注入导致重复
    if not history_msg or not isinstance(history_msg[0], SystemMessage):
        history_msg = [SystemMessage(OVER_ALL_PROMPT)] + history_msg

    # 防御性清理：如果消息列表中存在有 tool_calls 的 AI 消息
    # 但后续没有足够的 ToolMessage 跟随，则移除该 tool_calls
    # 防止 OpenAI API 400 错误 (insufficient tool messages)
    cleaned = []
    pending_tool_ids = set()
    pending_ai_idx = None  # 记录在 cleaned 中对应 AIMessage 的索引
    for msg in history_msg:
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            pending_tool_ids = {tc['id'] for tc in msg.tool_calls}
            pending_ai_idx = len(cleaned)  # 记录这个 AIMessage 在 cleaned 里的位置
            cleaned.append(msg)
        elif hasattr(msg, 'tool_call_id') and msg.tool_call_id:
            if msg.tool_call_id in pending_tool_ids:
                pending_tool_ids.discard(msg.tool_call_id)
                cleaned.append(msg)
            else:
                # 没有对应 tool_calls 的 ToolMessage — 丢弃
                pass
        else:
            # 普通消息（System/Human/AI 无 tool_calls）
            # 如果前面还有未匹配的 tool_calls，说明这些工具调用被丢弃了
            if pending_tool_ids:
                pending_tool_ids.clear()
                pending_ai_idx = None
            cleaned.append(msg)

    # 如果末尾还有未匹配的 tool_calls，找到对应的 AIMessage 移除它们
    if pending_tool_ids and pending_ai_idx is not None:
        from langchain_core.messages import AIMessage
        orphan = cleaned[pending_ai_idx]
        valid_tool_calls = [tc for tc in orphan.tool_calls if tc['id'] not in pending_tool_ids]
        cleaned[pending_ai_idx] = AIMessage(
            content=orphan.content or "",
            tool_calls=valid_tool_calls,
            additional_kwargs=orphan.additional_kwargs,
            response_metadata=orphan.response_metadata,
        )

    llm_output=await tool_model.ainvoke(cleaned)

    return {
        "messages":[llm_output],
    }

async def router(parent_state:ParentState)->Command[Literal["tool_node","__end__"]]:
    last_msg = parent_state['messages'][-1]
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
        return Command(goto="tool_node")
    return Command(goto="__end__", update={
        "output": parent_state['messages'][-1].content
    })


builder = StateGraph(state_schema=ParentState,input_state_schema=input_state,output_state_schema=output_state,private_state_schema=private_state)

builder.add_node("llm_node", llm_node,timeout=50,retry_policy=retry_policy)
builder.add_node("router", router)

# 封装 ToolNode，确保 tool_calls 与 ToolMessage 一一对应
class LoggingToolNode:
    def __init__(self, tools):
        self._tool_node = ToolNode(tools=tools)

    async def __call__(self, state, config=None):
        return await self._tool_node.ainvoke(state, config)

builder.add_node("tool_node", LoggingToolNode(PARENT_TOOLS), timeout=120, retry_policy=retry_policy)


builder.add_edge(START, "llm_node")
builder.add_edge("llm_node", "router",)
builder.add_edge("tool_node","llm_node")



async def ai_response(input:str,thread_id:str):
    async with AsyncPostgresSaver.from_conn_string(CHECKPOINTER_DATABASE_URL) as saver:
        await saver.setup()
        graph = builder.compile(checkpointer=saver)
        config = {
            "configurable": {
                "thread_id": thread_id
            },
            "recursion_limit": 100,
        }
        try:
            async for r in graph.astream(
                {"input": input, "messages": [HumanMessage(content=input)]},
                config=config, stream_mode="messages"
            ):
                yield r
        except GraphRecursionError as e:
            logger.info(f"Graph recursion error: {e}")