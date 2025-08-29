"""配置文件"""
import os
from typing import Optional
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()


class Config:
    """应用配置类"""
    
    # Redis配置
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT"))
    REDIS_DB: int = int(os.getenv("REDIS_DB"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # 任务配置
    TASK_EXPIRE_SECONDS: int = int(os.getenv("TASK_EXPIRE_SECONDS", "3600"))  # 默认1小时
    
    # AI API配置
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "qianwen")  # openai, claude, qianwen
    
    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Claude配置
    CLAUDE_API_KEY: Optional[str] = os.getenv("CLAUDE_API_KEY")
    CLAUDE_BASE_URL: str = os.getenv("CLAUDE_BASE_URL", "https://api.anthropic.com")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
    
    # 通义千问配置
    QIANWEN_API_KEY: Optional[str] = os.getenv("QIANWEN_API_KEY")
    QIANWEN_BASE_URL: str = os.getenv("QIANWEN_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
    QIANWEN_MODEL: str = os.getenv("QIANWEN_MODEL", "qwen-turbo")
    
    
    # API配置
    API_TITLE: str = "AI应用后端接口"
    API_DESCRIPTION: str = "提供中译英、英译中、总结等AI功能"
    API_VERSION: str = "1.0.0"


config = Config()
