"""AI应用后端接口主入口"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from routers import functions, translation, summary, tasks
from utils.logger import logger
import traceback

# 创建FastAPI应用
app = FastAPI(
    title="AI应用后端接口",
    description="提供中译英、英译中、总结等AI功能",
    version="1.0.0"
)

# 添加自定义JSON解析中间件
from utils.json_middleware import JSONCleanupMiddleware

app.add_middleware(JSONCleanupMiddleware)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加错误处理器
from utils.error_handlers import register_error_handlers

register_error_handlers(app)

# 注册路由
app.include_router(functions.router)
app.include_router(translation.router)
app.include_router(summary.router)
app.include_router(tasks.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
