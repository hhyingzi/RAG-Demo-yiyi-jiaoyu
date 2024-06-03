# 需要更改的唯一文件是 actions.py ，我们在其中定义一个自定义操作以将 LlamaIndex 与 NeMo Guardrails 集成。
from typing import Optional
from nemoguardrails.actions import action
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.base.response.schema import StreamingResponse
from app.engine.index import get_index_and_query_engine


query_engine_cache = None

def init():
    global query_engine_cache  

    if query_engine_cache is not None:
        print('Using cached query engine')
        return query_engine_cache

    query_engine_cache = get_index_and_query_engine()

    return query_engine_cache

def get_query_response(query_engine: BaseQueryEngine, query: str) -> str:
    """
    Function to query based on the query_engine and query string passed in.
    """
    response = query_engine.query(query)
    if isinstance(response, StreamingResponse):
        typed_response = response.get_response()
    else:
        typed_response = response
    response_str = typed_response.response
    if response_str is None:
        return ""
    return response_str

@action(is_system_action=True)
async def user_query(context: Optional[dict] = None):
    """
    Function to invoke the query_engine to query user message.
    """
    user_message = context.get("user_message")
    print('user_message is ', user_message)
    query_engine = init()
    return get_query_response(query_engine, user_message) 
