"""
文本预处理工具模块
提供统一的文本清理和预处理功能，确保JSON安全性
"""

import json
import re
from typing import Optional
from utils.logger import logger


class TextProcessor:
    """文本处理器类"""
    
    @staticmethod
    def clean_user_input(text: str) -> str:
        """
        基础清理：移除或转义特殊字符
        
        Args:
            text: 要清理的文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 替换双引号（JSON结构的关键符号）
        cleaned = text.replace('"', '\\"')
        # 处理单引号（避免不必要的干扰）
        cleaned = cleaned.replace("'", "\\'")
        # 处理换行符和制表符
        cleaned = cleaned.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        # 处理反斜杠
        cleaned = cleaned.replace('\\', '\\\\')
        
        return cleaned
    
    @staticmethod
    def deep_clean_text(text: str) -> str:
        """
        进阶处理：过滤不可见字符，但保留中文字符
        
        Args:
            text: 要清理的文本
            
        Returns:
            深度清理后的文本
        """
        if not text:
            return ""
        
        # 保留基本可见字符、中文字符和常用标点符号，过滤控制字符
        # \u4e00-\u9fff 是中文字符范围
        # \u3000-\u303f 是中文标点符号范围
        # \uff00-\uffef 是全角字符范围
        cleaned = re.sub(r'[^\x20-\x7E\s\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', '', text)
        # 去除多余空白，但保留基本的段落结构
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
    
    @staticmethod
    def prepare_user_input_for_ai(user_input: str) -> str:
        """
        处理用户输入，确保可安全序列化为JSON
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            处理后可安全用于JSON的文本
        """
        if not isinstance(user_input, str):
            return ""
        
        # 1. 深度清理
        cleaned = TextProcessor.deep_clean_text(user_input)
        
        try:
            # 2. 测试序列化是否成功
            test_payload = {"text": cleaned}
            json.dumps(test_payload, ensure_ascii=False)
            logger.debug(f"文本预处理完成，原长度: {len(user_input)}, 处理后长度: {len(cleaned)}")
            return cleaned
        except json.JSONDecodeError as e:
            logger.warning(f"JSON序列化测试失败: {e}，使用基础清理方法")
            # 3. 极端情况：使用基础清理
            cleaned = TextProcessor.clean_user_input(user_input)
            try:
                test_payload = {"text": cleaned}
                json.dumps(test_payload, ensure_ascii=False)
                return cleaned
            except json.JSONDecodeError:
                logger.error(f"文本包含无法处理的特殊字符，原文: {user_input[:100]}...")
                return "用户输入包含无法处理的特殊字符"
    
    @staticmethod
    def preprocess_text(text: str) -> str:
        """
        预处理文本，使用新的安全方法
        
        Args:
            text: 要处理的原始文本
            
        Returns:
            处理后的清洁文本
        """
        return TextProcessor.prepare_user_input_for_ai(text)
    
    @staticmethod
    def clean_control_characters(text: str, preserve_newlines: bool = True) -> str:
        """
        清理文本中的控制字符
        
        Args:
            text: 要清理的文本
            preserve_newlines: 是否保留换行符
            
        Returns:
            清理后的文本
        """
        if not text:
            return text
        
        if preserve_newlines:
            # 保留换行符、回车符和制表符，移除其他控制字符
            cleaned_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        else:
            # 移除所有控制字符
            cleaned_text = re.sub(r'[\x00-\x1F\x7F]', '', text)
        
        return cleaned_text
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        标准化空白字符
        
        Args:
            text: 要处理的文本
            
        Returns:
            标准化后的文本
        """
        if not text:
            return text
        
        # 将多个连续的空格合并为单个空格
        text = re.sub(r' +', ' ', text)
        
        # 将多个连续的制表符合并为单个制表符
        text = re.sub(r'\t+', '\t', text)
        
        return text
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """
        截断文本到指定长度
        
        Args:
            text: 要截断的文本
            max_length: 最大长度
            suffix: 截断后的后缀
            
        Returns:
            截断后的文本
        """
        if not text or len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix


# 便捷函数
def preprocess_text(text: str) -> str:
    """预处理文本的便捷函数"""
    return TextProcessor.preprocess_text(text)


def clean_control_characters(text: str, preserve_newlines: bool = True) -> str:
    """清理控制字符的便捷函数"""
    return TextProcessor.clean_control_characters(text, preserve_newlines)


def normalize_whitespace(text: str) -> str:
    """标准化空白字符的便捷函数"""
    return TextProcessor.normalize_whitespace(text)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """截断文本的便捷函数"""
    return TextProcessor.truncate_text(text, max_length, suffix)
