"""
AI服务模块
提供翻译和总结功能，支持多种AI服务提供商
"""

import asyncio
from typing import AsyncGenerator

from services.ai_providers import AIProviderFactory
from utils.logger import logger
from utils.text_processor import preprocess_text


class AIService:
    """AI服务类，提供翻译和总结功能"""
    
    def __init__(self):
        """初始化AI服务"""
        self.provider = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """初始化AI服务提供商"""
        try:
            self.provider = AIProviderFactory.create_provider()
            logger.info(f"AI服务提供商初始化成功: {self.provider.__class__.__name__}")
        except Exception as e:
            logger.error(f"AI服务提供商初始化失败: {e}")
            self.provider = None
    

    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            翻译后的文本
        """
        logger.info(f"翻译请求: {source_lang} -> {target_lang}")
        
        # 预处理文本
        cleaned_text = preprocess_text(text)
        
        if not self.provider:
            logger.warning("AI服务提供商未初始化，使用模拟翻译")
            return await self._mock_translate(cleaned_text, source_lang, target_lang)
        
        try:
            result = await self.provider.translate(cleaned_text, source_lang, target_lang)
            logger.info("翻译完成")
            return result
        except Exception as e:
            logger.error(f"翻译失败: {e}，使用模拟翻译")
            return await self._mock_translate(cleaned_text, source_lang, target_lang)
    
    async def summarize_text(self, text: str) -> str:
        """
        总结文本
        
        Args:
            text: 要总结的文本
            
        Returns:
            总结后的文本
        """
        logger.info("总结请求")
        
        # 预处理文本
        cleaned_text = preprocess_text(text)
        
        if not self.provider:
            logger.warning("AI服务提供商未初始化，使用模拟总结")
            return await self._mock_summarize(cleaned_text)
        
        try:
            result = await self.provider.summarize(cleaned_text)
            logger.info("总结完成")
            return result
        except Exception as e:
            logger.error(f"总结失败: {e}，使用模拟总结")
            return await self._mock_summarize(cleaned_text)
    
    async def translate_stream(self, text: str, source_lang: str, target_lang: str) -> AsyncGenerator[str, None]:
        """
        流式翻译
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Yields:
            翻译结果的片段
        """
        logger.info(f"流式翻译请求: {source_lang} -> {target_lang}")
        
        # 预处理文本
        cleaned_text = preprocess_text(text)
        
        if not self.provider:
            logger.warning("AI服务提供商未初始化，使用模拟流式翻译")
            async for chunk in self._mock_translate_stream(cleaned_text, source_lang, target_lang):
                logger.debug(f"模拟流式翻译输出: {chunk}")
                yield chunk
            return
        
        try:
            chunk_count = 0
            async for chunk in self.provider.translate_stream(cleaned_text, source_lang, target_lang):
                chunk_count += 1
                logger.debug(f"AI流式翻译输出 #{chunk_count}: {chunk}")
                yield chunk
            logger.info(f"流式翻译完成，共输出 {chunk_count} 个片段")
        except Exception as e:
            logger.error(f"流式翻译失败: {e}，使用模拟流式翻译")
            async for chunk in self._mock_translate_stream(cleaned_text, source_lang, target_lang):
                logger.debug(f"降级模拟流式翻译输出: {chunk}")
                yield chunk
    
    async def summarize_stream(self, text: str) -> AsyncGenerator[str, None]:
        """
        流式总结
        
        Args:
            text: 要总结的文本
            
        Yields:
            总结结果的片段
        """
        logger.info("流式总结请求")
        
        # 预处理文本
        cleaned_text = preprocess_text(text)
        
        if not self.provider:
            logger.warning("AI服务提供商未初始化，使用模拟流式总结")
            async for chunk in self._mock_summarize_stream(cleaned_text):
                yield chunk
            return
        
        try:
            async for chunk in self.provider.summarize_stream(cleaned_text):
                yield chunk
        except Exception as e:
            logger.error(f"流式总结失败: {e}，使用模拟流式总结")
            async for chunk in self._mock_summarize_stream(cleaned_text):
                yield chunk
    
    # 模拟实现（作为降级方案）
    async def _mock_translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """模拟翻译实现"""
        await asyncio.sleep(1)
        if source_lang == "中文" and target_lang == "英文":
            return f"[模拟EN] {text}"
        elif source_lang == "英文" and target_lang == "中文":
            return f"[模拟中文] {text}"
        else:
            return f"[模拟{target_lang}] {text}"
    
    async def _mock_summarize(self, text: str) -> str:
        """模拟总结实现"""
        await asyncio.sleep(1.5)
        return f"模拟总结: {text[:50]}{'...' if len(text) > 50 else ''}"
    
    async def _mock_translate_stream(self, text: str, source_lang: str, target_lang: str) -> AsyncGenerator[str, None]:
        """模拟流式翻译实现"""
        if source_lang == "中文" and target_lang == "英文":
            result = f"[模拟EN] {text}"
        elif source_lang == "英文" and target_lang == "中文":
            result = f"[模拟中文] {text}"
        else:
            result = f"[模拟{target_lang}] {text}"
        
        words = result.split()
        for word in words:
            await asyncio.sleep(0.1)
            yield word + " "
    
    async def _mock_summarize_stream(self, text: str) -> AsyncGenerator[str, None]:
        """模拟流式总结实现"""
        result = f"模拟总结: {text[:50]}{'...' if len(text) > 50 else ''}"
        words = result.split()
        for word in words:
            await asyncio.sleep(0.1)
            yield word + " "


# 创建全局实例
ai_service = AIService()
