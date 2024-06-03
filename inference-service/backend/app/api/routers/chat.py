from typing import List

from fastapi import APIRouter, HTTPException, status
from llama_index.core.llms import MessageRole
from pydantic import BaseModel
from nemoguardrails import LLMRails, RailsConfig

chat_router = r = APIRouter()

class _Message(BaseModel):
    role: MessageRole
    content: str

class _ChatData(BaseModel):
    messages: List[_Message]

@r.post("")
async def chat(data: _ChatData):

    if len(data.messages) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有提供消息",
        )
    lastMessage = data.messages.pop()
    if lastMessage.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="最后一个消息必须来自用户",
        )

    config = RailsConfig.from_path("./app/config")
    rails = LLMRails(config)

    prompt1 = "请用中文回答以下问题：问题：" 
    prompt2 = "回答问题后，引导用户对模型已经学习过的内容提问" 
    prompt=prompt1 + lastMessage.content

    response = await rails.generate_async(prompt)
    if  response == str("I'm sorry, I can't respond to that."):
        response = str("对不起，我不知道。")

    return response
