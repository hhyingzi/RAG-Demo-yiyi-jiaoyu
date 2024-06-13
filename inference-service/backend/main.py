from dotenv import load_dotenv

load_dotenv()

import logging
import os, sys
import uvicorn
from app.api.routers.chat import chat_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# FastAPI是一个现代化的Python Web框架，用于构建高性能的Web应用程序和API。通过 app 变量来使用其功能。
app = FastAPI()

# 如果环境变量"ENVIRONMENT"未设置，则默认使用开发模式
environment = os.getenv("ENVIRONMENT", "dev")  
# 开发模式，对 FastAPI 的跨域中间件进行设置，允许所有源的跨域资源共享。
if environment == "dev":
    logger = logging.getLogger("uvicorn")
    logger.warning("Running in development mode - allowing CORS for all origins")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 当应用程序收到匹配"/api/chat"前缀的请求时，将会使用 chat_router中定义的路由处理逻辑来处理这些请求。
app.include_router(chat_router, prefix="/api/chat")


if __name__ == "__main__":
    # 使用 uvicorn（一个异步服务器）来运行FastAPI应用程序。
    # 参数app指示web实例位于名为main的模块中，名称是app。参数reload指示在代码修改后自动重新启动服务器。
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
