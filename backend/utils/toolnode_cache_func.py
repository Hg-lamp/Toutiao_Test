import json
from langchain_core.messages import ToolMessage
from langgraph.cache.base import FullKey
from langgraph.cache.memory import InMemoryCache
from loguru import logger

CACHE=InMemoryCache()
TOOL_CACHE_NS=("tool_cache",)
async def wrap_tool_call(request,execute):
    tool_name=request.tool_call["name"]
    tool_args = json.dumps(request.tool_call["args"],sort_keys=True)
    tool_call_id=request.runtime.tool_call_id

    #工具名和代入参数作为键来判断是否重复调用
    cache_key:FullKey=(TOOL_CACHE_NS,f"{tool_name}::{tool_args}")
    cache=await CACHE.aget([cache_key])

    #判断缓存命中
    if cache_key in cache:
        logger.info(f"缓存命中{tool_name}")
        tool_msg=ToolMessage(content=cache[cache_key],tool_call_id=tool_call_id)
    else:
        tool_msg= await execute(request)
        await CACHE.aset({cache_key:(tool_msg.content,3600)})
    return tool_msg