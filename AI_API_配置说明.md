# AI API 配置说明

## 概述

本项目已集成多种AI服务提供商，支持OpenAI、Claude、通义千问等。您需要配置相应的API密钥才能使用真实的AI功能。

## 支持的AI服务商

### 1. OpenAI (要钱)
- **模型**: GPT-3.5-turbo, GPT-4等
- **获取方式**: https://platform.openai.com/api-keys
- **配置项**:
  - `OPENAI_API_KEY`: API密钥
  - `OPENAI_BASE_URL`: API基础URL (默认: https://api.openai.com/v1)
  - `OPENAI_MODEL`: 使用的模型 (默认: gpt-3.5-turbo)

### 2. Claude (要钱)
- **模型**: Claude-3-haiku, Claude-3-sonnet等
- **获取方式**: https://console.anthropic.com/
- **配置项**:
  - `CLAUDE_API_KEY`: API密钥
  - `CLAUDE_BASE_URL`: API基础URL (默认: https://api.anthropic.com)
  - `CLAUDE_MODEL`: 使用的模型 (默认: claude-3-haiku-20240307)

### 3. 通义千问 (这个好，有免费额度)
- **模型**: qwen-turbo, qwen-plus等
- **获取方式**: https://dashscope.console.aliyun.com/
- **配置项**:
  - `QIANWEN_API_KEY`: API密钥
  - `QIANWEN_BASE_URL`: API基础URL (默认: https://dashscope.aliyuncs.com/api/v1)
  - `QIANWEN_MODEL`: 使用的模型 (默认: qwen-turbo)

## 配置步骤

### 1. 编辑.env文件
```bash
# 选择AI服务提供商
AI_PROVIDER=openai

# 配置OpenAI (示例)
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# 或者配置Claude
# AI_PROVIDER=claude
# CLAUDE_API_KEY=your-claude-api-key-here

# 或者配置通义千问
# AI_PROVIDER=qianwen
# QIANWEN_API_KEY=your-qianwen-api-key-here
```

### 2. 安装依赖
```bash
# 安装新的AI相关依赖
pip install openai anthropic httpx aiohttp
```

### 3. 重启应用
```bash
uvicorn main:app --reload
```

## 降级机制

如果AI API配置失败或调用出错，系统会自动降级到模拟模式：
- ✅ 应用正常运行
- ✅ 接口正常响应
- ⚠️ 返回模拟结果（带"模拟"标识）

## 常见问题

### Q: API密钥无效怎么办？
A: 检查密钥是否正确，是否有足够的配额，网络是否能访问API服务。

### Q: 如何切换AI服务商？
A: 修改`.env`文件中的`AI_PROVIDER`值，重启应用即可。

### Q: 可以同时配置多个服务商吗？
A: 可以配置多个密钥，但同时只能使用一个（由`AI_PROVIDER`决定）。

### Q: 如何查看详细错误信息？
A: 查看应用日志，所有AI API调用错误都会被记录。

## 安全建议

1. **不要提交.env文件到版本控制**
2. **定期轮换API密钥**
3. **设置API使用限额**
4. **监控API使用情况**
5. **在生产环境使用环境变量而非文件配置**
