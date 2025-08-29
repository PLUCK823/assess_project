"""数据模型包"""
from .requests import TranslationRequest, SummaryRequest
from .responses import TaskResponse, TaskResult

__all__ = [
    "TranslationRequest",
    "SummaryRequest", 
    "TaskResponse",
    "TaskResult"
]
