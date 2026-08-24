from loguru import logger

from backend.utils.retriever import retriever


class Rag:
    def __init__(self,topic:str):
        self.topic=topic
        self.retriever=retriever

    async def run(self):
        try:
            result_docs=await self.retriever.ainvoke(self.topic)
        except Exception as e:
            logger.info("rag检索出错{}",e)
            return []
        result = [doc.page_content for doc in result_docs]
        return result
    def __repr__(self):
        return f'<{self.retriever.config_schema()}>'