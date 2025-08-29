"""
JSON清理中间件
处理请求中的JSON格式问题，确保文本内容的安全性
"""

import json
import re
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

from utils.logger import logger
from utils.text_processor import TextProcessor


class JSONCleanupMiddleware(BaseHTTPMiddleware):
    """JSON清理中间件，处理包含特殊字符的JSON请求"""
    
    async def dispatch(self, request: Request, call_next):
        """处理请求的主要逻辑"""
        if request.headers.get("content-type", "").startswith("application/json"):
            body = await request.body()
            try:
                # 先尝试解析JSON看是否有问题
                body_str = body.decode('utf-8')
                
                # 尝试直接解析原始JSON
                try:
                    json.loads(body_str)
                    # 如果解析成功，直接使用原始请求体
                    response = await call_next(request)
                    return response
                except json.JSONDecodeError:
                    # JSON解析失败，需要清理
                    pass
                
                # 使用新的安全JSON处理方法
                try:
                    # 解析原始JSON获取数据
                    data = json.loads(body_str)
                    
                    # 如果包含text字段，使用安全的文本处理方法
                    if isinstance(data, dict) and 'text' in data:
                        # 使用新的文本预处理方法
                        data['text'] = TextProcessor.prepare_user_input_for_ai(data['text'])
                        # 重新序列化为安全的JSON
                        cleaned_body = json.dumps(data, ensure_ascii=False)
                    else:
                        cleaned_body = body_str
                        
                except json.JSONDecodeError:
                    # 如果原始JSON解析失败，尝试修复
                    try:
                        # 提取text字段内容
                        text_match = re.search(r'"text"\s*:\s*"(.*?)"', body_str, re.DOTALL)
                        if text_match:
                            original_text = text_match.group(1)
                            # 使用安全的文本处理
                            safe_text = TextProcessor.prepare_user_input_for_ai(original_text)
                            # 重构整个JSON
                            cleaned_body = re.sub(
                                r'"text"\s*:\s*".*?"',
                                f'"text": "{safe_text}"',
                                body_str,
                                flags=re.DOTALL
                            )
                        else:
                            # 如果找不到text字段，使用原始内容
                            cleaned_body = body_str
                    except Exception as e:
                        logger.error(f"JSON修复失败: {e}")
                        cleaned_body = body_str
                
                # 验证清理后的JSON是否有效
                json.loads(cleaned_body)
                
                # 重新构造请求
                scope = request.scope.copy()
                scope["body"] = cleaned_body.encode('utf-8')
                
                # 创建新的receive函数
                async def receive():
                    return {
                        "type": "http.request",
                        "body": cleaned_body.encode('utf-8'),
                        "more_body": False
                    }
                
                # 创建新的请求对象
                new_request = StarletteRequest(scope, receive)
                
                response = await call_next(new_request)
                return response
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {e}")
                logger.error(f"原始请求体长度: {len(body_str) if 'body_str' in locals() else 'unknown'}")
                # 返回JSON解析错误
                return JSONResponse(
                    status_code=422,
                    content={
                        "success": False,
                        "message": "JSON格式错误",
                        "error": str(e)
                    }
                )
            except Exception as e:
                logger.error(f"JSON清理失败: {e}")
        
        response = await call_next(request)
        return response
