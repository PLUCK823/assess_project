"""请求数据模型"""
from pydantic import BaseModel
from typing import Optional


class TranslationRequest(BaseModel):
    """翻译请求模型"""
    text: str
    source_lang: str = "auto"
    target_lang: str = "英文"


class SummaryRequest(BaseModel):
    """总结请求模型"""
    text: str
    max_length: Optional[int] = 200
