from langchain_core.tools import tool

from backend.config.search_engine import SearXNG

#搜索工具

#由于tavily使用需要另外配置apikey，所以使用SearXNG
@tool
async def searxng_search_engine(query:str):
    """
    搜索工具
    写入查询问题，对新闻，咨询，实时信息，网络信息进行搜索，返回搜索到的内容
    :param query: 需要搜索的内容
    :return: 返回搜索到的结果
    """
    return await SearXNG.arun(query,engines=["baidu","bing"])

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


TOOLS=[growth_rate,searxng_search_engine]

tool_map={
    "growth_rate":growth_rate,
    "searxng_search_engine":searxng_search_engine
}