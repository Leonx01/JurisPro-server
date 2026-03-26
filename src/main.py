from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse


# 获取数据库连接 URL

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """在应用启动时预加载模型"""
    # logging.info("🚀 开始加载模型")
    # # 获取数据库会话，并确保正确释放
    # db = MysqlClient.get_instance()
    # LLMFactory.load_config_from_db(db)  # 直接调用类方法，无需实例化
    # logging.info("✅ 模型加载完成")
    # LLMFactory.print_models()
    yield  # 进入 FastAPI 运行状态


app = FastAPI(lifespan=lifespan)
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

from fastapi.middleware.cors import CORSMiddleware

# 允许跨域请求
origins = [
    "http://localhost:9000",
    "http://localhost:9001",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from src.api import auth_api
from src.api import redis_demo_api
from src.api import user_api
from src.api import app_api
from src.api import test_api
from src.api import sys_api
from src.api import knowledge_api
from src.api import llm_api
from src.api import document_api
from src.api import prompt_api
from src.api import function_api
from src.api import chat_api
from src.api import retrieve_api
from src.api import role_api
from src.api import menu_api
app.include_router(menu_api.router)
app.include_router(retrieve_api.router)
app.include_router(chat_api.router)
app.include_router(function_api.router)
app.include_router(knowledge_api.router)
app.include_router(user_api.router)
app.include_router(redis_demo_api.router)
app.include_router(auth_api.router)
app.include_router(app_api.router)

app.include_router(test_api.router)
app.include_router(sys_api.router)
app.include_router(llm_api.router)
app.include_router(document_api.router)
app.include_router(prompt_api.router)
app.include_router(role_api.router)

import os

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")
from src.exceptions.exception import AppException


# 异常处理
@app.exception_handler(AppException)
async def app_exception_handler(_request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.code,
        content=exc.to_dict()
    )
