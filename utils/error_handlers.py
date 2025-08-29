"""
错误处理模块
提供统一的异常处理和错误响应
"""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from utils.logger import logger


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    请求验证错误处理器
    
    Args:
        request: FastAPI请求对象
        exc: 验证异常
        
    Returns:
        JSONResponse: 格式化的错误响应
    """
    logger.error(f"请求验证失败: {request.url}")
    logger.error(f"验证错误详情: {exc.errors()}")
    
    # 安全地获取请求体，避免编码问题
    try:
        body = await request.body()
        body_str = body.decode('utf-8', errors='replace')
        logger.error(f"请求体: {body_str}")
    except Exception as e:
        logger.error(f"无法读取请求体: {e}")
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "请求参数验证失败",
            "errors": exc.errors()
        }
    )


def register_error_handlers(app):
    """
    注册所有错误处理器到FastAPI应用
    
    Args:
        app: FastAPI应用实例
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
