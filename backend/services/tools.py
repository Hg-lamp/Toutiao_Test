from langchain_core.tools import tool
from langchain_tavily import TavilySearch

tavily= TavilySearch()

@tool
async def growth_rate(now:float,before:float):
    """
    计算今年相比于上一年的增长率
    :param now: 今年的数值
    :param before: 上一年的数值
    :return: 返回增长率
    """
    return f'{(now/before)*100}%'

# 异步化 TavilySearch——确保它支持 ainvoke（TavilySearch 底层是 httpx，原生支持异步）
# 不需要额外改动，langchain_tavily 的 TavilySearch 已实现 ainvoke

TOOLS=[tavily,growth_rate]

tool_map={
    "growth_rate":growth_rate,
    "tavily_search":tavily
}