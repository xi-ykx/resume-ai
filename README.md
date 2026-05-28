# AI Resume Optimizer

## 项目简介

AI Resume Optimizer 是一个面向求职场景的 AI 简历优化应用。用户输入目标岗位和原始简历内容后，后端会调用 DeepSeek 大模型，生成优化后的简历表达、修改理由和关键词建议，前端负责提交表单并分区展示结果。

这个项目适合作为 AI 应用工程师作品集项目展示：它覆盖了从前端交互、后端 API、Prompt 设计、模型调用、结构化输出、流式响应、错误处理、安全边界到基础测试的完整小闭环。

## 功能截图

> 截图占位：后续可以在这里放前端页面截图。

```text
docs/images/home-page.png
```

> 截图占位：后续可以在这里放结构化优化结果截图。

```text
docs/images/json-result.png
```

> 截图占位：后续可以在这里放流式输出效果截图。

```text
docs/images/stream-result.png
```

## 核心功能

- 输入目标岗位和原始简历内容。
- 使用 DeepSeek API 对简历进行 AI 优化。
- 返回优化后的简历、修改理由和关键词建议。
- 支持结构化 JSON 返回，方便前端分区展示。
- 支持流式输出，让用户逐步看到生成结果。
- 支持复制优化结果。
- 支持基础历史记录，保存最近优化结果到本地 `data/history.json`。
- 提供健康检查接口和历史记录接口。
- 对空输入、超长输入、AI 调用失败和空返回做基础错误处理。

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 后端框架 | FastAPI |
| 数据校验 | Pydantic |
| AI 调用 | DeepSeek API, OpenAI Python SDK |
| 环境变量 | python-dotenv |
| 服务运行 | Uvicorn |
| 前端 | HTML, CSS, JavaScript, Fetch API |
| 流式输出 | FastAPI `StreamingResponse` |
| 测试 | Python unittest, FastAPI TestClient, mock |
| 本地数据 | JSON 文件 |

## 项目亮点

- **完整 AI 应用闭环**：从用户输入到模型调用，再到结构化展示和复制结果，覆盖真实 AI 产品的基本链路。
- **结构化输出设计**：通过 Prompt 约束模型返回 JSON，前端可以稳定展示 `optimized_resume`、`reasons` 和 `problem_analysis`。
- **流式响应体验**：支持边生成边返回，减少用户等待感。
- **安全意识明确**：API Key 仅在后端读取，不进入前端；日志只记录请求状态和简历长度，不记录完整简历。
- **错误处理清晰**：对空输入、超长输入、AI 超时、AI 返回为空和格式异常返回明确错误。
- **逐步模块化**：配置已拆分到 `config.py`，AI 模型调用已拆分到 `services/ai_client.py`，为后续继续重构打基础。
- **可测试性提升**：基础 API 测试使用 mock，避免真实调用 AI API，降低测试成本。

## 项目结构

```text
.
├── README.md
├── AGENTS.md
├── config.py
├── day06.py
├── index.html
├── requirements.txt
├── .env.example
├── .gitignore
├── docs/
│   ├── api.md
│   └── day03-backend-notes.md
├── services/
│   └── ai_client.py
├── tests/
│   └── test_api.py
└── test/
    ├── day03.py
    ├── day04.py
    └── day05.py
```

## 本地运行

### 1. 克隆项目

```bash
git clone https://github.com/xi-ykx/resume-ai.git
cd resume-ai
```

### 2. 创建并激活虚拟环境

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env`，然后填写自己的 DeepSeek API Key。

```text
DEEPSEEK_API_KEY=your_api_key_here
```

不要把真实 API Key 写入 README、前端代码、测试代码或提交到 GitHub。

### 5. 启动后端

```bash
uvicorn day06:app --reload
```

默认地址：

```text
http://127.0.0.1:8000
```

### 6. 打开前端

直接用浏览器打开：

```text
index.html
```

输入目标岗位和简历内容后，可以测试结构化优化和流式优化。

### 7. 运行测试

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

当前测试会 mock AI 调用，不需要真实请求 DeepSeek API。

## API 文档

完整 API 说明见：[docs/api.md](docs/api.md)

核心接口：

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/health` | 健康检查 |
| `POST` | `/polish-resume-json` | 结构化简历优化 |
| `POST` | `/polish-resume-stream` | 流式简历优化 |
| `GET` | `/history` | 读取最近 10 条本地历史记录 |

## 安全说明

- `.env` 用于保存真实 API Key，不允许提交到 GitHub。
- `.env.example` 只保留占位符，不包含真实密钥。
- API Key 只在后端读取，不暴露给 `index.html`。
- 日志不记录完整简历内容，最多记录简历长度和错误类型。
- `data/` 已加入 `.gitignore`，避免本地历史简历被误提交。
- `/history` 接口只允许本机访问，避免公网直接读取简历历史。
- 当前项目适合本地学习和作品集演示，生产部署前还需要增加鉴权、限流、HTTPS、持久化数据库和更严格的 CORS 配置。

## 后续计划

- 将路由拆分到 `routes/resume.py`。
- 将简历业务逻辑拆分到 `services/resume_service.py`。
- 增加历史记录前端页面。
- 增加删除历史记录和清空历史记录功能。
- 增加请求取消、加载状态和字数统计。
- 增加更完整的异常类型和错误码。
- 增加部署文档和线上环境配置说明。
- 增加截图和演示 GIF。

## 面试时可以讲的技术点

- 如何设计一个 AI 应用的端到端流程：前端输入、后端校验、Prompt 构造、模型调用、结果展示。
- 为什么 API Key 必须放在后端环境变量中，而不能写进前端。
- 如何通过 Prompt 要求模型返回稳定 JSON，并用 Pydantic 约束接口返回格式。
- 如何处理 AI API 的失败、超时、空返回和格式异常。
- 为什么要使用流式输出，以及 `StreamingResponse` 的基本工作方式。
- 如何避免日志泄露用户简历隐私。
- 如何用 mock 测试 AI 接口，避免测试依赖真实模型和真实 API Key。
- 如何从单文件项目逐步演进到分层结构，而不是一次性大重构。
