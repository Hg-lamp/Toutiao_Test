from backend.config.redis_vector import retriever_database


class Retriever:
    def __init__(self,count:int=2):
        self.retriever=retriever_database.as_retriever( search_kwargs ={"k":count})

    async def ainvoke(self,query:str):
        return await self.retriever.ainvoke(query)

    def config_schema(self):
        return self.retriever.config_schema()