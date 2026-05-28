# AI Resume Optimizer

AI Resume Optimizer 是一个基于智谱 AI 大模型的简历优化工具。用户输入目标岗位和原始简历内容后，系统会分析简历表达问题，生成更贴近招聘场景的优化版本，并解释修改原因。

这个项目展示了一个完整的小型 AI 应用闭环：前端表单交互、FastAPI 后端接口、环境变量管理、AI SDK 调用、结构化 JSON 响应、流式输出和基础错误处理。

## 项目亮点

- **面向真实场景**：围绕简历优化这一明确业务需求设计输入、输出和提示词。
- **双模式输出**：支持结构化 JSON 返回，也支持流式文本返回。
- **安全边界清晰**：API Key 仅通过 `.env` 配置，不暴露到前端或文档。
- **输入校验**：后端会拒绝空简历、空岗位等无效请求，避免无意义调用 AI。
- **错误处理**：AI 调用失败、超时、返回为空时返回明确 JSON 错误。
- **日志记录**：记录请求开始、结束、错误类型和简历长度，不记录完整简历内容。

## 功能概览

- 输入目标岗位和原始简历内容。
- 分析原始简历存在的问题。
- 基于用户提供的事实优化简历表达。
- 解释为什么这样修改。
- 提供结构化结果，方便前端分区展示。
- 提供流式输出，让用户逐步看到生成结果。
- 提供健康检查接口，方便确认后端服务状态。

## 技术栈

| 分类 | 技术 |
| --- | --- |
| 后端框架 | FastAPI |
| 数据校验 | Pydantic |
| AI 调用 | 智谱 AI SDK `zai-sdk` |
| 环境变量 | python-dotenv |
| 服务运行 | Uvicorn |
| 前端 | HTML, CSS, JavaScript, Fetch API |

## 项目结构

```text
.
├── README.md                  # 项目介绍和运行说明
├── AGENTS.md                  # 协作规则和项目约束
├── day06.py                   # FastAPI 后端主文件
├── index.html                 # 前端页面
├── requirements.txt           # Python 直接依赖
├── .env.example               # 环境变量模板，不包含真实密钥
├── .gitignore                 # Git 忽略规则
├── docs/
│   ├── api.md                 # API 文档
│   └── day03-backend-notes.md # 后端学习笔记
└── test/
    ├── day03.py
    ├── day04.py
    └── day05.py
```

## 本地运行

### 1. 克隆并进入项目

```bash
git clone https://github.com/xi-ykx/resume-ai.git
cd resume-ai
```

### 2. 安装依赖

建议先创建并激活虚拟环境，然后安装依赖：

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，并填写你自己的智谱 AI API Key：

```text
ZHIPUAI_API_KEY=your_api_key_here
```

不要把真实 API Key 写入 README、前端代码或提交到 GitHub。

### 4. 启动后端

```bash
uvicorn day06:app --reload
```

默认服务地址：

```text
http://127.0.0.1:8000
```

### 5. 检查服务状态

浏览器访问：

```text
http://127.0.0.1:8000/health
```

预期返回：

```json
{
  "status": "ok"
}
```

### 6. 打开前端

直接用浏览器打开：

```text
index.html
```

输入目标岗位和简历内容后，可以分别测试“结构化优化简历”和“流式优化简历”。

## API 文档

完整接口说明见：

[docs/api.md](docs/api.md)

当前核心接口：

- `GET /health`：健康检查
- `POST /polish-resume-json`：结构化简历优化
- `POST /polish-resume-stream`：流式简历优化

## 环境变量

| 变量名 | 必填 | 说明 |
| --- | --- | --- |
| `ZHIPUAI_API_KEY` | 是 | 智谱 AI API Key，仅供后端调用模型使用 |

项目提供 `.env.example` 作为模板。真实 `.env` 文件已在 `.gitignore` 中忽略。

## 安全说明

- 不提交 `.env`。
- 不在前端保存或传输 API Key。
- 不在日志中记录完整简历内容。
- 错误响应不暴露 API Key 或底层敏感信息。
- 当前 CORS 配置适合本地开发，生产部署时应限制允许访问的前端域名。

## 后续计划

- 增加复制优化结果功能。
- 增加输入字数统计和最大长度限制。
- 增加请求取消功能，优化流式输出体验。
- 增加单元测试和接口测试。
- 增加更细粒度的错误码。
- 为生产部署收紧 CORS、增加鉴权和限流。
