"""Redis客户端配置"""
import redis
import json
import logging
from typing import Optional, Any
from config import config

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis客户端封装类"""
    
    def __init__(self):
        self.client = None
        self._memory_storage = {}
        self._initialized = False
    
    def _initialize(self):
        """延迟初始化Redis连接"""
        if self._initialized:
            return
            
        try:
            redis_config = {
                'host': config.REDIS_HOST,
                'port': config.REDIS_PORT,
                'db': config.REDIS_DB,
                'decode_responses': True,
                'socket_connect_timeout': 3,
                'socket_timeout': 3
            }
            if config.REDIS_PASSWORD:
                redis_config['password'] = config.REDIS_PASSWORD
                
            self.client = redis.Redis(**redis_config)
            self.client.ping()
            logger.info(f"Redis连接成功: {config.REDIS_HOST}:{config.REDIS_PORT}")
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}，使用内存存储")
            self.client = None
        
        self._initialized = True
    
    def is_connected(self) -> bool:
        self._initialize()
        return self.client is not None
    
    def set_json(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        self._initialize()
        try:
            if self.client:
                json_str = json.dumps(value, ensure_ascii=False, default=str)
                return self.client.set(key, json_str, ex=ex)
            else:
                self._memory_storage[key] = value
                return True
        except Exception as e:
            logger.error(f"存储失败: {e}")
            return False
    
    def get_json(self, key: str) -> Optional[Any]:
        self._initialize()
        try:
            if self.client:
                json_str = self.client.get(key)
                return json.loads(json_str) if json_str else None
            else:
                return self._memory_storage.get(key)
        except Exception as e:
            logger.error(f"获取失败: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        self._initialize()
        try:
            if self.client:
                return bool(self.client.delete(key))
            else:
                return self._memory_storage.pop(key, None) is not None
        except Exception as e:
            logger.error(f"删除失败: {e}")
            return False
    
    def keys(self, pattern: str = "*") -> list:
        self._initialize()
        try:
            if self.client:
                return self.client.keys(pattern)
            else:
                return list(self._memory_storage.keys())
        except Exception as e:
            logger.error(f"获取键列表失败: {e}")
            return []
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """异步set方法，兼容异步调用"""
        self._initialize()
        try:
            if self.client:
                return self.client.set(key, value, ex=ex)
            else:
                self._memory_storage[key] = value
                return True
        except Exception as e:
            logger.error(f"异步存储失败: {e}")
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """异步get方法，兼容异步调用"""
        self._initialize()
        try:
            if self.client:
                return self.client.get(key)
            else:
                return self._memory_storage.get(key)
        except Exception as e:
            logger.error(f"异步获取失败: {e}")
            return None


# 全局Redis客户端实例
redis_client = RedisClient()
