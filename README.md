# AI Resume Optimizer

AI Resume Optimizer 是一个基于智谱 AI 大模型的简历优化工具。用户输入目标岗位和原始简历内容后，系统会分析简历存在的问题，并生成更适合招聘场景的优化表达和修改理由。

## 项目功能

- 根据目标岗位分析原始简历内容的问题。
- 基于用户提供的事实优化简历表达。
- 返回结构化 JSON 结果，方便前端分区展示。
- 支持流式输出，让用户逐步看到 AI 生成内容。
- 提供健康检查接口，方便确认后端服务是否正常。

## 技术栈

- Python 3.9+
- FastAPI
- Pydantic
- Uvicorn
- python-dotenv
- 智谱 AI SDK：`zai-sdk`
- 前端：HTML、CSS、JavaScript、Fetch API

## 文件结构

```text
D:\api-test\day02
├── AGENTS.md                  # 项目协作和修改规则
├── CLAUDE.md                  # 项目说明备份或其他助手规则
├── README.md                  # 项目说明文档
├── day06.py                   # 后端主代码，包含 FastAPI 接口和 AI 调用逻辑
├── index.html                 # 前端页面
├── requirements.txt           # Python 依赖列表
├── docs/
│   └── day03-backend-notes.md # 后端学习笔记
└── test/
    ├── day03.py
    ├── day04.py
    └── day05.py
```

本地还可能存在以下文件或目录，它们不应该提交：

- `.env`
- `.venv/`
- `__pycache__/`
- `.idea/`

## 本地运行方法

### 1. 安装依赖

在项目根目录运行：

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件，并配置智谱 AI API Key：

```text
ZHIPUAI_API_KEY="你的智谱AI API Key"
```

注意：不要把真实 API Key 写入 README，也不要提交 `.env` 文件。

### 3. 启动后端服务

```bash
uvicorn day06:app --reload
```

默认服务地址：

```text
http://127.0.0.1:8000
```

### 4. 检查后端是否启动成功

浏览器访问：

```text
http://127.0.0.1:8000/health
```

或在 PowerShell 中运行：

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

预期返回：

```json
{"status":"ok"}
```

### 5. 打开前端页面

用浏览器打开：

```text
D:\api-test\day02\index.html
```

然后输入目标岗位和简历内容，点击页面上的按钮进行测试。

## 环境变量说明

| 变量名 | 是否必需 | 说明 |
| --- | --- | --- |
| `ZHIPUAI_API_KEY` | 是 | 智谱 AI API Key，用于后端调用大模型。 |

示例：

```text
ZHIPUAI_API_KEY="请在本地填写真实密钥，不要提交"
```

## 当前功能

后端当前提供以下接口：

- `GET /`：返回 API 启动提示。
- `GET /health`：健康检查。
- `POST /polish-resume-json`：返回结构化简历优化结果。
- `POST /polish-resume-stream`：返回流式简历优化文本。

前端当前支持：

- 输入目标岗位。
- 输入原始简历内容。
- 调用结构化优化接口。
- 调用流式优化接口。
- 展示 AI 返回结果。
- 请求过程中按钮显示“处理中...”，请求结束后恢复原文字。

## 后续计划

- 增加输入字数统计和长度限制。
- 增加复制优化结果按钮。
- 增加请求取消功能，尤其是流式输出场景。
- 优化错误提示，区分后端未启动、参数错误、AI 调用失败等情况。
- 限制 CORS 来源，避免生产环境使用 `allow_origins=["*"]`。
- 增加接口鉴权和限流，控制调用成本。
- 增加自动化测试，覆盖参数校验、JSON 解析和接口返回。
- 整理依赖列表，移除不再使用的依赖。
