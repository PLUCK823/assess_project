"""翻译相关路由"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import ValidationError
from schemas.requests import TranslationRequest
from schemas.responses import TranslationResponse, AsyncTaskResponse, TaskResponse, TaskResult
from services.ai_service import ai_service
from utils.logger import logger
from data.redis_keys import RedisKeys
from utils.redis_client import redis_client
import json
import uuid
from datetime import datetime

router = APIRouter(prefix="/api", tags=["translation"])

# ai_service 已在 services.ai_service 中导入


@router.post("/translate", summary="同步翻译接口")
async def translate_sync(request: TranslationRequest):
    """同步翻译接口"""
    try:
        result = await ai_service.translate_text(request.text, request.source_lang, request.target_lang)
        
        return {
            "success": True,
            "data": {
                "original_text": request.text,
                "translated_text": result,
                "source_lang": request.source_lang,
                "target_lang": request.target_lang
            },
            "message": "翻译成功"
        }
    except Exception as e:
        logger.error(f"翻译失败: {e}")
        raise HTTPException(status_code=500, detail=f"翻译失败: {str(e)}")


@router.post("/translate/async", summary="异步翻译任务提交")
async def translate_async(request: TranslationRequest, background_tasks: BackgroundTasks):
    """提交异步翻译任务"""
    task_id = str(uuid.uuid4())
    
    # 创建任务记录
    task_result = TaskResult(
        task_id=task_id,
        status="pending",
        created_at=datetime.now().isoformat()
    )
    # 将任务存储到Redis
    await redis_client.set(
        RedisKeys.task_key(task_id),
        task_result.model_dump_json(),
        ex=3600  # 1小时过期
    )
    
    # 添加后台任务
    background_tasks.add_task(
        _process_translation_task, 
        task_id, 
        request.text, 
        request.source_lang, 
        request.target_lang
    )
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="翻译任务已提交，请使用task_id轮询结果"
    )


@router.post("/translate/stream", summary="流式翻译接口")
async def translate_stream(request: TranslationRequest):
    """流式翻译接口 - 使用Server-Sent Events"""
    try:
        logger.info(f"收到流式翻译请求: {request.source_lang} -> {request.target_lang}")
        
        async def event_stream():
            try:
                # 发送开始事件
                yield f"data: {json.dumps({'type': 'start', 'message': '开始翻译'}, ensure_ascii=False)}\n\n"
                
                # 获取流式翻译结果
                chunk_count = 0
                full_result = ""
                
                async for chunk in ai_service.translate_stream(request.text, request.source_lang, request.target_lang):
                    if chunk and chunk.strip():
                        chunk_count += 1
                        full_result += chunk.strip()
                        logger.debug(f"流式数据 #{chunk_count}: '{chunk.strip()}'")
                        
                        # 发送数据块，清理控制字符
                        clean_chunk = chunk.strip().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                        yield f"data: {json.dumps({'type': 'chunk', 'content': clean_chunk}, ensure_ascii=False)}\n\n"
                
                # 发送完成事件
                yield f"data: {json.dumps({'type': 'done', 'message': '翻译完成', 'full_result': full_result}, ensure_ascii=False)}\n\n"
                logger.info(f"流式翻译完成，共处理 {chunk_count} 个片段")
                
            except Exception as e:
                logger.error(f"流式翻译过程中出错: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "*",
            }
        )
        
    except Exception as e:
        logger.error(f"流式翻译初始化失败: {e}")
        raise HTTPException(status_code=500, detail=f"流式翻译失败: {str(e)}")


async def _process_translation_task(task_id: str, text: str, source_lang: str, target_lang: str):
    """处理翻译任务的后台函数"""
    try:
        # 更新任务状态为处理中
        task_result = TaskResult(
            task_id=task_id,
            status="processing",
            created_at=datetime.now().isoformat()
        )
        await redis_client.set(
            RedisKeys.task_key(task_id),
            task_result.model_dump_json(),
            ex=3600
        )
        
        # 执行翻译
        result = await ai_service.translate_text(text, source_lang, target_lang)
        
        # 更新任务状态为完成
        task_result = TaskResult(
            task_id=task_id,
            status="completed",
            result=result,
            created_at=datetime.now().isoformat(),
            completed_at=datetime.now().isoformat()
        )
        await redis_client.set(
            RedisKeys.task_key(task_id),
            task_result.model_dump_json(),
            ex=3600
        )
        
    except Exception as e:
        logger.error(f"处理翻译任务失败: {e}")
        # 更新任务状态为失败
        task_result = TaskResult(
            task_id=task_id,
            status="failed",
            error=str(e),
            created_at=datetime.now().isoformat(),
            completed_at=datetime.now().isoformat()
        )
        await redis_client.set(
            RedisKeys.task_key(task_id),
            task_result.model_dump_json(),
            ex=3600
        )
