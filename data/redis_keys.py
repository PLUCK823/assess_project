"""Redis键名定义"""

class RedisKeys:
    """Redis键名管理类"""
    
    # 任务相关键
    TASK_PREFIX = "ai_task:"
    TASK_COUNTER = "ai_task_counter"
    
    # 统计相关键
    STATS_PREFIX = "ai_stats:"
    DAILY_REQUESTS = "daily_requests"
    TOTAL_REQUESTS = "total_requests"
    
    @classmethod
    def task_key(cls, task_id: str) -> str:
        """生成任务键名"""
        return f"{cls.TASK_PREFIX}{task_id}"
    
    @classmethod
    def stats_key(cls, date: str) -> str:
        """生成统计键名"""
        return f"{cls.STATS_PREFIX}{date}"
