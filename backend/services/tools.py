import numexpr as ne
from langchain_core.tools import tool
from backend.config.search_engine import SearXNG
from backend.services.Rag import Rag

#搜索工具

#由于tavily使用需要另外配置apikey，所以使用SearXNG
@tool
async def searxng_search_engine(query:str):
    """
    互联网搜索工具
    写入查询问题，对新闻，咨询，实时信息，网络信息进行搜索，返回搜索到的内容
    :param query: 需要搜索的内容
    :return: 返回搜索到的结果
    """
    try:
        return await SearXNG.arun(query,engines=["baidu","bing"])
    except Exception as e:
        return f"搜索失败: {str(e)}"

#测试的一个工具
@tool
async def calculator(expression: str):
    """
    计算数学表达式
    :param expression: 数学表达式，如 "3 + 5 * 2", "sqrt(16)", "2 ** 10"
    """
    return ne.evaluate(expression).item()

@tool
async def rag_search(topic:str,count:int=2)->list[str]:
    """
    检索公务员考试（公考）知识库的专用工具。
    当用户的问题明确涉及公务员考试、行测、申论、公考知识点时使用。
    不要在无关话题（如日常聊天、写诗、讲笑话、天气查询等）使用此工具。
    :param topic: 需要检索的内容关键词
    :param count:需要检索返回的结果数量，默认为2
    :return: 返回检索到的结果（列表形式）
    """
    rag= Rag(search_count=count)
    return await rag.arun(topic)



@tool
async def agent(task:str)->str:
    """
    任务下发工具（一个任务对应一个agent）
    一般在长难任务时候调用，用于下发单个任务给子agent。
    子agent是一个独立ReAct的agent，能够独立完成任务，最后将结果返回给主agent。
    如果需要处理多个任务，主agent可以多次调用此工具，每次传入一个任务。
    每个调用都会返回一个独立的 ToolMessage，确保 tool_calls 与 ToolMessage 一一对应。

    :param task: 需要处理的单个任务描述
    :return: 返回处理结果
    """
    from backend.agent.child_graph import child_output
    try:
        result = await child_output(task)
        return f"任务的结果为:\n{result}\n"
    except Exception as e:
        return f"任务执行失败: {str(e)}"


PARENT_TOOLS=[calculator,searxng_search_engine,agent,rag_search]
CHILD_TOOLS=[calculator,searxng_search_engine,rag_search]
