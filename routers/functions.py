"""功能相关路由"""
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["functions"])

# 支持的功能列表
supported_functions = [
    {
        "id": "zh_to_en",
        "name": "中译英",
        "description": "将中文翻译为英文",
        "type": "translation"
    },
    {
        "id": "en_to_zh", 
        "name": "英译中",
        "description": "将英文翻译为中文",
        "type": "translation"
    },
    {
        "id": "summarize",
        "name": "文本总结",
        "description": "对输入文本进行总结",
        "type": "summary"
    }
]


@router.get("/functions", summary="获取所有功能列表")
async def get_functions():
    """获取系统支持的所有AI功能列表"""
    return {
        "success": True,
        "data": supported_functions,
        "message": "获取功能列表成功"
    }
