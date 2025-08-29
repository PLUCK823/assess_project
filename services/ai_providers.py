"""
AI服务提供商适配器
支持OpenAI、Claude、通义千问等多种AI服务
"""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, Optional
import httpx
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from config.settings import config
from utils.logger import logger


class AIProviderBase(ABC):
    """AI服务提供商基类"""
    
    @abstractmethod
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """翻译文本"""
        pass
    
    @abstractmethod
    async def summarize(self, text: str) -> str:
        """总结文本"""
        pass
    
    @abstractmethod
    async def translate_stream(self, text: str, source_lang: str, target_lang: str) -> AsyncGenerator[str, None]:
        """流式翻译"""
        pass
    
    @abstractmethod
    async def summarize_stream(self, text: str) -> AsyncGenerator[str, None]:
        """流式总结"""
        pass


class OpenAIProvider(AIProviderBase):
    """OpenAI服务提供商"""
    
    def __init__(self):
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY环境变量未设置")
        
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL
        )
        self.model = config.OPENAI_MODEL
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """翻译文本"""
        try:
            prompt = f"请将以下{source_lang}文本翻译成{target_lang}，只返回翻译结果：\n\n{text}"
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI翻译失败: {e}")
            raise
    
    async def summarize(self, text: str) -> str:
        """总结文本"""
        try:
            prompt = f"请对以下文本进行简洁的总结：\n\n{text}"
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI总结失败: {e}")
            raise
    
    async def translate_stream(self, text: str, source_lang: str, target_lang: str) -> AsyncGenerator[str, None]:
        """流式翻译"""
        try:
            prompt = f"请将以下{source_lang}文本翻译成{target_lang}，只返回翻译结果：\n\n{text}"
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI流式翻译失败: {e}")
            raise
    
    async def summarize_stream(self, text: str) -> AsyncGenerator[str, None]:
        """流式总结"""
        try:
            prompt = f"请对以下文本进行简洁的总结：\n\n{text}"
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI流式总结失败: {e}")
            raise


class ClaudeProvider(AIProviderBase):
    """Claude服务提供商"""
    
    def __init__(self):
        if not config.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY环境变量未设置")
        
        self.client = AsyncAnthropic(api_key=config.CLAUDE_API_KEY)
        self.model = config.CLAUDE_MODEL
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """翻译文本"""
        try:
            prompt = f"请将以下{source_lang}文本翻译成{target_lang}，只返回翻译结果：\n\n{text}"
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Claude翻译失败: {e}")
            raise
    
    async def summarize(self, text: str) -> str:
        """总结文本"""
        try:
            prompt = f"请对以下文本进行简洁的总结：\n\n{text}"
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Claude总结失败: {e}")
            raise
    
    async def translate_stream(self, text: str, source_lang: str, target_lang: str) -> AsyncGenerator[str, None]:
        """流式翻译"""
        try:
            prompt = f"请将以下{source_lang}文本翻译成{target_lang}，只返回翻译结果：\n\n{text}"
            
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Claude流式翻译失败: {e}")
            raise
    
    async def summarize_stream(self, text: str) -> AsyncGenerator[str, None]:
        """流式总结"""
        try:
            prompt = f"请对以下文本进行简洁的总结：\n\n{text}"
            
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Claude流式总结失败: {e}")
            raise


class QianwenProvider(AIProviderBase):
    """通义千问服务提供商"""
    
    def __init__(self):
        if not config.QIANWEN_API_KEY:
            raise ValueError("QIANWEN_API_KEY环境变量未设置")
        
        self.api_key = config.QIANWEN_API_KEY
        self.base_url = config.QIANWEN_BASE_URL
        self.model = config.QIANWEN_MODEL
        
        # 同步接口使用OpenAI兼容模式
        from openai import AsyncOpenAI
        self.openai_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    
    async def _make_request(self, prompt: str) -> str:
        """发送请求到通义千问API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "temperature": 0.3,
                "result_format": "message"
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/services/aigc/text-generation/generation",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            # 处理新的响应格式
            if "output" in result:
                if "choices" in result["output"] and result["output"]["choices"]:
                    return result["output"]["choices"][0]["message"]["content"]
                elif "text" in result["output"]:
                    return result["output"]["text"]
            return "API响应格式错误"
    
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """翻译文本 - 使用OpenAI兼容模式"""
        try:
            prompt = f"请将以下{source_lang}文本翻译成{target_lang}，只返回翻译结果：\n\n{text}"
            
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"通义千问翻译失败: {e}")
            raise
    
    async def summarize(self, text: str) -> str:
        """总结文本 - 使用OpenAI兼容模式"""
        try:
            prompt = f"请对以下文本进行简洁的总结：\n\n{text}"
            
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"通义千问总结失败: {e}")
            raise
    
    async def translate_stream(self, text: str, source_lang: str, target_lang: str) -> AsyncGenerator[str, None]:
        """流式翻译 - 使用OpenAI兼容模式"""
        try:
            prompt = f"请将以下{source_lang}文本翻译成{target_lang}，只返回翻译结果：\n\n{text}"
            
            stream = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"通义千问流式翻译失败: {e}")
            raise
    
    async def summarize_stream(self, text: str) -> AsyncGenerator[str, None]:
        """流式总结 - 使用OpenAI兼容模式"""
        try:
            prompt = f"请对以下文本进行简洁的总结：\n\n{text}"
            
            stream = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"通义千问流式总结失败: {e}")
            raise


class AIProviderFactory:
    """AI服务提供商工厂类"""
    
    _providers = {
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
        "qianwen": QianwenProvider,
    }
    
    @classmethod
    def create_provider(cls, provider_name: str = None) -> AIProviderBase:
        """创建AI服务提供商实例"""
        if provider_name is None:
            provider_name = config.AI_PROVIDER
        
        if provider_name not in cls._providers:
            raise ValueError(f"不支持的AI服务提供商: {provider_name}")
        
        # 只在首次创建时检查API密钥状态
        if not hasattr(cls, '_logged_api_status'):
            cls._log_api_key_status()
            cls._logged_api_status = True
        
        try:
            return cls._providers[provider_name]()
        except Exception as e:
            logger.error(f"创建AI服务提供商失败: {e}")
            raise
    
    @classmethod
    def _log_api_key_status(cls):
        """记录API密钥配置状态"""
        logger.info("=== AI API密钥配置状态 ===")
        logger.info(f"选择的AI服务提供商: {config.AI_PROVIDER}")
        
        # OpenAI状态
        openai_key = config.OPENAI_API_KEY
        if openai_key and openai_key != "your_openai_api_key_here":
            logger.info(f"✅ OpenAI API密钥: 已配置 (sk-...{openai_key[-8:]})")
        else:
            logger.warning("❌ OpenAI API密钥: 未配置")
        
        # Claude状态
        claude_key = config.CLAUDE_API_KEY
        if claude_key and claude_key != "your_claude_api_key_here":
            logger.info(f"✅ Claude API密钥: 已配置 (...{claude_key[-8:]})")
        else:
            logger.warning("❌ Claude API密钥: 未配置")
        
        # 通义千问状态
        qianwen_key = config.QIANWEN_API_KEY
        if qianwen_key and qianwen_key != "your_qianwen_api_key_here":
            logger.info(f"✅ 通义千问 API密钥: 已配置 (...{qianwen_key[-8:]})")
        else:
            logger.warning("❌ 通义千问 API密钥: 未配置")
        
        logger.info("========================")
    
    @classmethod
    def get_available_providers(cls) -> list:
        """获取可用的AI服务提供商列表"""
        available = []
        for name, provider_class in cls._providers.items():
            try:
                provider_class()
                available.append(name)
            except ValueError as e:
                logger.debug(f"{name} 服务提供商不可用: {e}")
                continue
        return available
