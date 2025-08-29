# AI 应用后端接口

这是一个基于 FastAPI 的 AI 应用后端接口，提供中译英、英译中、总结等功能。采用模块化架构设计，代码结构清晰，易于维护和扩展。

## 项目结构

```
assess_project/
├── main.py                 # 应用入口点
├── .env                    # 环境变量配置
├── .gitignore              # Git忽略文件
├── pyproject.toml          # 项目配置和依赖管理
├── uv.lock                 # 依赖锁定文件
├── AI_API_配置说明.md       # AI API配置说明文档
├── config/                 # 配置文件夹
│   ├── __init__.py
│   └── settings.py         # 应用配置
├── data/                   # 数据相关文件夹
│   ├── __init__.py
│   └── redis_keys.py       # Redis键名管理
├── schemas/                # 数据模型
│   ├── __init__.py
│   ├── requests.py         # 请求模型
│   └── responses.py        # 响应模型
├── routers/                # 路由模块
│   ├── __init__.py
│   ├── functions.py        # 功能列表路由
│   ├── translation.py      # 翻译相关路由
│   ├── summary.py          # 总结相关路由
│   ├── tasks.py            # 任务管理路由
│   └── health.py           # 健康检查路由
├── services/               # 业务逻辑服务
│   ├── __init__.py
│   ├── ai_service.py       # AI模型调用服务
│   ├── ai_providers.py     # AI服务提供商实现
│   └── task_service.py     # 任务管理服务
├── utils/                  # 工具函数
│   ├── __init__.py
│   ├── logger.py           # 日志配置
│   ├── redis_client.py     # Redis客户端
│   ├── text_processor.py   # 文本预处理工具
│   ├── json_middleware.py  # JSON清理中间件
│   └── error_handlers.py   # 错误处理器
└── README.md
```

## 功能特性

- ✅ 获取所有功能列表接口
- ✅ 同步调用功能接口（翻译、总结）
- ✅ 异步任务执行和轮询机制
- ✅ 流式返回接口支持
- ✅ 完整的错误处理和日志记录
- ✅ 模块化架构设计
- ✅ 代码分层清晰

## 安装和运行

1. 安装依赖：

```bash
uv sync
```

2. 启动服务：

```bash
uvicorn main:app --reload
```

服务将在 http://localhost:8000 启动

## API 接口文档

### 1. 获取功能列表

```
GET /api/functions
```

### 2. 同步翻译接口

```
POST /api/translate
Content-Type: application/json

{
    "text": "你好世界",
    "source_lang": "zh",
    "target_lang": "en"
}
```

### 3. 同步总结接口

```
POST /api/summarize
Content-Type: application/json

{
    "text": "这是一段需要总结的长文本...",
    "max_length": 200
}
```

### 4. 异步翻译任务提交

```
POST /api/translate/async
Content-Type: application/json

{
    "text": "你好世界",
    "source_lang": "zh",
    "target_lang": "en"
}
```

### 5. 异步总结任务提交

```
POST /api/summarize/async
Content-Type: application/json

{
    "text": "这是一段需要总结的长文本...",
    "max_length": 200
}
```

### 6. 轮询任务结果

```
GET /api/task/{task_id}
```

### 7. 流式翻译接口

```
POST /api/translate/stream
Content-Type: application/json

{
    "text": "你好世界",
    "source_lang": "zh",
    "target_lang": "en"
}
```

### 8. 流式总结接口

```
POST /api/summarize/stream
Content-Type: application/json

{
    "text": "这是一段需要总结的长文本...",
    "max_length": 200
}
```

## 测试示例

### 使用 curl 测试

1. 获取功能列表：

```bash
curl -X GET "http://localhost:8000/api/functions"
```

2. 同步翻译：

```bash
curl -X POST "http://localhost:8000/api/translate" \
  -H "Content-Type: application/json" \
  -d '{"text": "你好世界", "target_lang": "en"}'
```

3. 异步翻译：

```bash
# 提交任务
curl -X POST "http://localhost:8000/api/translate/async" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World", "target_lang": "zh"}'

# 轮询结果（使用返回的task_id）
curl -X GET "http://localhost:8000/api/task/{task_id}"
```

4. 流式翻译：

```bash
curl -X POST "http://localhost:8000/api/translate/stream" \
  -H "Content-Type: application/json" \
  -d '{"text": "你好世界", "target_lang": "en"}' \
  --no-buffer
```

## 接口响应格式

### 成功响应

```json
{
    "success": true,
    "data": {...},
    "message": "操作成功"
}
```

### 错误响应

```json
{
  "detail": "错误信息"
}
```

## 大模型集成
w
- OpenAI GPT API
- Anthropic Claude API
- 阿里通义千问 API

## Redis 集成

项目已集成 Redis 作为任务存储后端，支持以下特性：

### Redis 配置

通过环境变量配置 Redis 连接：

```bash
# 可选环境变量
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_DB=0
export REDIS_PASSWORD=your_password  # 如果需要
export TASK_EXPIRE_SECONDS=3600      # 任务过期时间（秒）
```

### 自动降级机制

- 如果 Redis 连接失败，系统会自动降级到内存存储
- 不影响 API 正常使用，只是任务数据不会持久化

### 启动 Redis 服务

在 Windows 上启动 Redis：

```bash
# 如果已安装Redis
redis-server

# 或使用Docker
docker run -d -p 6379:6379 redis:latest
```

## 注意事项

~~1. 目前数据存储在代码中，没有使用任何数据库存储，异步任务无法查询结果~~

1. 已集成 Redis 存储，异步任务可正常查询结果
2. 大模型调用为伪代码，需要替换为真实 API
3. 所有接口都包含完整的错误处理和日志记录
4. Redis 连接失败时会自动降级到内存存储
