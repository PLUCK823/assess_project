"""任务管理相关路由"""
from fastapi import APIRouter, HTTPException
from services.task_service import TaskService

router = APIRouter(prefix="/api", tags=["tasks"])
task_service = TaskService()


@router.get("/task/{task_id}", summary="轮询任务结果")
async def get_task_result(task_id: str):
    """轮询异步任务结果"""
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return {
        "success": True,
        "data": task.dict(),
        "message": "获取任务状态成功"
    }
