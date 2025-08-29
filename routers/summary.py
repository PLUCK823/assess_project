"""总结相关路由"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import json
import uuid
from datetime import datetime
import logging

from schemas.requests import SummaryRequest
from schemas.responses import TaskResponse, TaskResult
from services.ai_service import ai_service
from utils.logger import logger
from data.redis_keys import RedisKeys
from utils.redis_client import redis_client

router = APIRouter(prefix="/api", tags=["summary"])


@router.post("/summarize", summary="同步总结接口")
async def summarize_sync(request: SummaryRequest):
    """同步总结接口"""
    try:
        result = await ai_service.summarize_text(request.text)
        
        return {
            "success": True,
            "data": {
                "original_text": request.text,
                "summary": result,
                "max_length": request.max_length
            },
            "message": "总结成功"
        }
    except Exception as e:
        logger.error(f"总结失败: {e}")
        raise HTTPException(status_code=500, detail=f"总结失败: {str(e)}")


@router.post("/summarize/async", summary="异步总结任务提交")
async def summarize_async(request: SummaryRequest, background_tasks: BackgroundTasks):
    """提交异步总结任务"""
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
        _process_summary_task,
        task_id,
        request.text
    )
    
    return TaskResponse(
        task_id=task_id,
        status="pending", 
        message="总结任务已提交，请使用task_id轮询结果"
    )


@router.post("/summarize/stream", summary="流式总结接口")
async def summarize_stream(request: SummaryRequest):
    """流式总结接口"""
    try:
        async def generate():
            yield "data: " + json.dumps({"status": "started", "message": "开始总结"}, ensure_ascii=False) + "\n\n"
            
            async for chunk in ai_service.summarize_stream(request.text):
                if chunk.strip():  # 只输出非空内容
                    clean_chunk = chunk.strip().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                    yield "data: " + json.dumps({"chunk": clean_chunk}, ensure_ascii=False) + "\n\n"
            
            yield "data: " + json.dumps({"status": "completed", "message": "总结完成"}, ensure_ascii=False) + "\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
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
        logger.error(f"流式总结失败: {e}")
        raise HTTPException(status_code=500, detail=f"流式总结失败: {str(e)}")


async def _process_summary_task(task_id: str, text: str):
    """处理总结任务的后台函数"""
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
        
        # 执行总结
        result = await ai_service.summarize_text(text)
        
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
        logger.error(f"处理总结任务失败: {e}")
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
