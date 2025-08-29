"""任务服务 - 处理异步任务管理"""
import logging
from datetime import datetime
from typing import Optional
from schemas import TaskResult
from .ai_service import AIService
from utils.redis_client import redis_client
from config import config
from data.redis_keys import RedisKeys

logger = logging.getLogger(__name__)


class TaskService:
    """任务服务类，处理异步任务管理"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def create_task(self, task_id: str, task_result: TaskResult):
        """创建任务"""
        key = RedisKeys.task_key(task_id)
        redis_client.set_json(key, task_result.dict(), ex=config.TASK_EXPIRE_SECONDS)
    
    def get_task(self, task_id: str) -> Optional[TaskResult]:
        """获取任务"""
        key = RedisKeys.task_key(task_id)
        task_data = redis_client.get_json(key)
        if task_data:
            return TaskResult(**task_data)
        return None
    
    def update_task(self, task_id: str, **updates):
        """更新任务状态"""
        task = self.get_task(task_id)
        if task:
            for key, value in updates.items():
                setattr(task, key, value)
            self.create_task(task_id, task)
    
    def get_tasks_count(self) -> int:
        """获取任务总数"""
        keys = redis_client.keys(f"{RedisKeys.TASK_PREFIX}*")
        return len(keys)
    
    async def process_translation_task(self, task_id: str, text: str, source_lang: str, target_lang: str):
        """异步处理翻译任务"""
        try:
            self.update_task(task_id, status="processing")
            
            # 构建提示词
            if target_lang == "en":
                prompt = f"请将以下中文翻译为英文：{text}"
            else:
                prompt = f"Please translate the following English to Chinese: {text}"
            
            result = await self.ai_service.call_ai_model(prompt, "translation")
            
            self.update_task(
                task_id, 
                status="completed",
                result=result,
                completed_at=datetime.now().isoformat()
            )
            
            logger.info(f"翻译任务 {task_id} 完成")
            
        except Exception as e:
            self.update_task(task_id, status="failed", error=str(e))
            logger.error(f"翻译任务 {task_id} 失败: {e}")

    async def process_summary_task(self, task_id: str, text: str, max_length: int):
        """异步处理总结任务"""
        try:
            self.update_task(task_id, status="processing")
            
            prompt = f"请对以下文本进行总结，限制在{max_length}字以内：{text}"
            result = await self.ai_service.call_ai_model(prompt, "summary")
            
            self.update_task(
                task_id,
                status="completed", 
                result=result,
                completed_at=datetime.now().isoformat()
            )
            
            logger.info(f"总结任务 {task_id} 完成")
            
        except Exception as e:
            self.update_task(task_id, status="failed", error=str(e))
            logger.error(f"总结任务 {task_id} 失败: {e}")
