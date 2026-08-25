from langchain_core.tools import tool
from langchain_tavily import TavilySearch
#搜索工具
tavily= TavilySearch()

#测试的一个工具
@tool
async def growth_rate(now:float,before:float):
    """
    计算今年相比于上一年的增长率
    :param now: 今年的数值
    :param before: 上一年的数值
    :return: 返回增长率
    """
    return f'{(now/before)*100}%'


TOOLS=[tavily,growth_rate]

tool_map={
    "growth_rate":growth_rate,
    "tavily_search":tavily
}