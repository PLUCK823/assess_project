"""日志配置工具"""
import logging
import sys


def setup_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """设置日志配置"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # 添加处理器到日志器
        logger.addHandler(console_handler)
        logger.setLevel(level)
    
    return logger


# 创建默认日志器实例
logger = setup_logger("ai_backend")
