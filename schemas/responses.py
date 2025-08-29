"""响应数据模型"""
from pydantic import BaseModel
from typing import Optional


class TaskResponse(BaseModel):
    """任务响应模型"""
    task_id: str
    status: str  # pending, processing, completed, failed
    message: str


class TaskResult(BaseModel):
    """任务结果模型"""
    task_id: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


class TranslationResponse(BaseModel):
    """翻译响应模型"""
    success: bool
    data: Optional[str] = None
    message: str


class AsyncTaskResponse(BaseModel):
    """异步任务响应模型"""
    task_id: str
    status: str
    message: str


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    message: str
    redis_status: str
    ai_status: Optional[str] = None
