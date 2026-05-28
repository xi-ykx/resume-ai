# Day 03 后端复习笔记：day06.py

## 1. 这个项目做什么

这个项目是一个 AI 简历润色助手。用户在前端页面 `index.html` 输入目标岗位和原始简历内容，后端 `day06.py` 接收请求后调用智谱 AI 模型，让 AI 分析简历问题、优化简历表达，并解释为什么这样修改。

当前项目有两种使用方式：

- Web 方式：启动 FastAPI 后端，再打开 `index.html` 调用接口。
- 命令行方式：直接运行 `python day06.py`，在终端输入目标岗位和简历内容。

## 2. day06.py 的整体流程

可以把 `day06.py` 理解成 5 个部分：

1. 加载环境变量，读取智谱 AI API Key。
2. 创建智谱 AI 客户端。
3. 创建 FastAPI Web 服务。
4. 定义请求数据、响应数据和 AI 调用函数。
5. 定义后端接口，让前端可以通过 HTTP 调用 AI 能力。

## 3. 环境变量和 AI 客户端

代码会从项目根目录的 `.env` 文件中加载环境变量，然后读取 `ZHIPUAI_API_KEY`。

如果没有配置这个变量，程序启动时会报错：

```python
raise ValueError("没有找到api，请检查.env文件")
```

读取到 API Key 后，会创建智谱 AI 客户端：

```python
client = ZhipuAiClient(api_key=api_key)
```

后面所有调用 AI 的地方，都是通过这个 `client` 完成的。

注意：`.env` 里保存的是敏感密钥，不应该读取、打印或提交。

## 4. FastAPI Web 服务

代码通过下面这一行创建 Web 应用：

```python
app = FastAPI()
```

启动命令通常是：

```bash
uvicorn day06:app --reload
```

含义是：

- `day06`：加载 `day06.py` 文件。
- `app`：使用文件里的 `app = FastAPI()` 对象。
- `--reload`：开发模式下自动重启，适合本地调试。

## 5. 请求模型 ResumeRequest

`ResumeRequest` 定义了前端请求后端时必须传什么数据：

```python
class ResumeRequest(BaseModel):
    job_target: str = Field(..., min_length=2, description="目标岗位")
    resume_text: str = Field(..., min_length=5, description="简历内容")
```

它要求请求体是这样的 JSON：

```json
{
  "job_target": "AI应用工程师",
  "resume_text": "我学过Python，会调用AI接口，做过一个聊天机器人。"
}
```

字段说明：

- `job_target`：目标岗位，至少 2 个字符。
- `resume_text`：简历内容，至少 5 个字符。

如果字段缺失或长度太短，FastAPI 会自动返回 `422` 参数校验错误。

## 6. 响应模型 ResumeJsonResponse

`ResumeJsonResponse` 定义了结构化接口返回给前端的数据格式：

```python
class ResumeJsonResponse(BaseModel):
    problem_analysis: list[str]
    optimized_resume: str
    reasons: list[str]
```

返回内容示例：

```json
{
  "problem_analysis": ["表达过于简单", "缺少岗位匹配度"],
  "optimized_resume": "具备 Python 基础和 AI 接口调用经验，曾完成聊天机器人项目实践。",
  "reasons": ["突出技能关键词", "让表达更贴近招聘场景"]
}
```

## 7. clean_json_text 的作用

AI 有时候会把 JSON 包在 Markdown 代码块里，例如：

````text
```json
{"problem_analysis": [], "optimized_resume": "...", "reasons": []}
```
````

但 Python 的 `json.loads()` 只能解析纯 JSON 字符串，不能解析 Markdown。所以 `clean_json_text()` 的作用是去掉开头和结尾的代码块标记。

## 8. 三个 AI 调用函数

### ask_ai

`ask_ai()` 是普通文本版本，主要用于命令行模式。

它会让 AI 按三段输出：

- 一、原始内容存在的问题
- 二、优化后的简历表达
- 三、为什么这样修改

### ask_ai_json

`ask_ai_json()` 是结构化 JSON 版本，供 `/polish-resume-json` 接口使用。

它要求 AI 只返回 JSON，然后代码会执行：

```python
data = json.loads(json_text)
```

如果 AI 返回的不是合法 JSON，这里就会报错。

### ask_ai_stream

`ask_ai_stream()` 是流式输出版本，供 `/polish-resume-stream` 接口使用。

它设置了：

```python
stream=True
```

这样模型生成一点内容，后端就可以先返回一点内容，前端也能逐步显示。

## 9. 当前后端接口

### GET /

用途：确认 API 服务已启动。

返回：

```json
{"message": "AI 简历润色助手 API 已启动"}
```

### GET /health

用途：健康检查。

返回：

```json
{"status": "ok"}
```

### POST /polish-resume-json

用途：结构化优化简历。

请求体：

```json
{
  "job_target": "目标岗位",
  "resume_text": "简历内容"
}
```

返回：

```json
{
  "problem_analysis": ["问题1", "问题2"],
  "optimized_resume": "优化后的简历表达",
  "reasons": ["理由1", "理由2"]
}
```

### POST /polish-resume-stream

用途：流式优化简历。

请求体：

```json
{
  "job_target": "目标岗位",
  "resume_text": "简历内容"
}
```

返回：纯文本流。前端会一边接收一边显示。

## 10. 容易报错的地方

- `.env` 没有配置 `ZHIPUAI_API_KEY`，后端无法启动。
- API Key 错误，AI 调用会失败。
- 网络异常或智谱 AI 服务异常，AI 调用会失败。
- AI 没有按要求返回 JSON，`json.loads()` 会失败。
- AI 返回 JSON 缺少必要字段，例如没有 `reasons`，构造响应时会失败。
- 前端传入的 `job_target` 或 `resume_text` 太短，FastAPI 会返回 `422`。
- 流式返回时，如果 SDK 返回结构变化，读取 `chunk.choices[0].delta` 可能失败。

## 11. 不适合直接上线的地方

- CORS 当前允许所有来源访问，生产环境应该限制为具体前端域名。
- 没有登录或鉴权，任何人都可以调用 AI 接口。
- 没有限流，可能被频繁调用导致费用升高。
- 没有输入长度上限，超长简历可能导致响应慢、费用高或模型失败。
- AI JSON 解析失败时，后端会把原始 AI 内容返回给前端，可能暴露用户简历内容。
- 缺少统一日志、错误处理和敏感信息脱敏。

## 12. 手动测试方法

启动后端：

```bash
uvicorn day06:app --reload
```

测试健康接口：

```bash
curl http://127.0.0.1:8000/health
```

预期返回：

```json
{"status":"ok"}
```

然后用浏览器打开 `index.html`，分别点击：

- 结构化优化简历
- 流式优化简历

观察页面是否正常显示 AI 返回结果。
