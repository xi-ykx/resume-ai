# API Reference

本文档面向开发者，说明 AI Resume Optimizer 当前后端接口。示例不包含真实 API Key。API Key 只应配置在后端 `.env` 文件中，前端请求不需要也不应该携带 API Key。

## Base URL

本地开发默认地址：

```text
http://127.0.0.1:8000
```

## 通用约定

- 请求体格式：`application/json`
- 普通 JSON 接口返回：`application/json`
- 流式接口成功返回：`text/plain; charset=utf-8`
- 错误响应格式由 FastAPI 返回，通常为：

```json
{
  "detail": "错误说明"
}
```

参数校验错误可能返回数组：

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "job_target"],
      "msg": "String should have at least 2 characters"
    }
  ]
}
```

## 数据模型

### ResumeRequest

用于两个简历优化接口。

```json
{
  "job_target": "AI应用工程师",
  "resume_text": "我学过 Python，会调用 AI 接口，做过一个聊天机器人。"
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `job_target` | string | 是 | 目标岗位，至少 2 个字符；全空格会被业务校验拒绝 |
| `resume_text` | string | 是 | 原始简历内容，不能是空字符串或全空格 |

### ResumeJsonResponse

`POST /polish-resume-json` 成功时返回。

```json
{
  "problem_analysis": ["问题1", "问题2"],
  "optimized_resume": "优化后的简历表达",
  "reasons": ["理由1", "理由2"]
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `problem_analysis` | string[] | 原始简历存在的问题 |
| `optimized_resume` | string | 优化后的简历文本 |
| `reasons` | string[] | 修改原因 |

## GET /

### 接口名称

API 启动提示

### 请求路径

```text
/
```

### 请求方法

```text
GET
```

### 请求示例

```js
const response = await fetch("http://127.0.0.1:8000/");
const data = await response.json();
console.log(data.message);
```

### 成功响应

状态码：`200`

```json
{
  "message": "AI 简历润色助手 API 已启动"
}
```

### 失败响应

服务未启动时，请求会在浏览器或 HTTP 客户端侧失败，后端不会返回业务 JSON。

## GET /health

### 接口名称

健康检查

### 请求路径

```text
/health
```

### 请求方法

```text
GET
```

### 请求示例

```js
const response = await fetch("http://127.0.0.1:8000/health");
const data = await response.json();
console.log(data.status);
```

PowerShell：

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

### 成功响应

状态码：`200`

```json
{
  "status": "ok"
}
```

### 失败响应

服务未启动时，请求会在浏览器或 HTTP 客户端侧失败。

## POST /polish-resume-json

### 接口名称

结构化优化简历

### 请求路径

```text
/polish-resume-json
```

### 请求方法

```text
POST
```

### 请求 JSON 示例

```json
{
  "job_target": "AI应用工程师",
  "resume_text": "我学过 Python，会调用 AI 接口，做过一个聊天机器人。"
}
```

### 前端调用示例

```js
const response = await fetch("http://127.0.0.1:8000/polish-resume-json", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    job_target: jobTarget,
    resume_text: resumeText
  })
});

if (!response.ok) {
  const errorData = await response.json();
  const message = Array.isArray(errorData.detail)
    ? errorData.detail[0]?.msg || "请求参数不正确"
    : errorData.detail || "请求失败";
  throw new Error(message);
}

const data = await response.json();
console.log(data.problem_analysis);
console.log(data.optimized_resume);
console.log(data.reasons);
```

### 成功响应

状态码：`200`

```json
{
  "problem_analysis": [
    "原始表达较简单，缺少与目标岗位的匹配说明。",
    "项目经历描述不够具体。"
  ],
  "optimized_resume": "具备 Python 基础和 AI 接口调用经验，曾完成聊天机器人项目实践，能够围绕业务需求实现基础 AI 应用功能。",
  "reasons": [
    "突出 Python 和 AI 接口调用能力。",
    "保留用户已提供事实，不新增不存在的经历。"
  ]
}
```

### 失败响应

简历内容为空或全空格，状态码：`400`

```json
{
  "detail": "简历内容不能为空，请填写原始简历内容。"
}
```

目标岗位为全空格且长度满足请求模型时，状态码：`400`

```json
{
  "detail": "目标岗位不能为空，请填写目标岗位。"
}
```

目标岗位为空字符串、长度不足或字段缺失时，状态码：`422`

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "job_target"],
      "msg": "String should have at least 2 characters"
    }
  ]
}
```

AI 服务调用失败，状态码：`502`

```json
{
  "detail": "AI 服务调用失败，请稍后重试。"
}
```

AI 服务请求超时，状态码：`504`

```json
{
  "detail": "AI 服务请求超时，请稍后重试。"
}
```

AI 返回为空，状态码：`502`

```json
{
  "detail": "AI 返回内容为空，请稍后重试。"
}
```

AI 返回格式异常，状态码：`502`

```json
{
  "detail": "AI 返回格式异常，请稍后重试。"
}
```

## POST /polish-resume-stream

### 接口名称

流式优化简历

### 请求路径

```text
/polish-resume-stream
```

### 请求方法

```text
POST
```

### 请求 JSON 示例

```json
{
  "job_target": "AI应用工程师",
  "resume_text": "我学过 Python，会调用 AI 接口，做过一个聊天机器人。"
}
```

### 前端调用示例

```js
const response = await fetch("http://127.0.0.1:8000/polish-resume-stream", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    job_target: jobTarget,
    resume_text: resumeText
  })
});

if (!response.ok) {
  const errorData = await response.json();
  const message = Array.isArray(errorData.detail)
    ? errorData.detail[0]?.msg || "请求参数不正确"
    : errorData.detail || "请求失败";
  throw new Error(message);
}

const reader = response.body.getReader();
const decoder = new TextDecoder("utf-8");

while (true) {
  const { done, value } = await reader.read();

  if (done) {
    break;
  }

  const chunk = decoder.decode(value, { stream: true });
  console.log(chunk);
}
```

### 成功响应

状态码：`200`

响应类型：`text/plain; charset=utf-8`

示例内容：

```text
一、原始内容存在的问题
原始表达较简单，缺少岗位匹配度说明。

二、优化后的简历表达
具备 Python 基础和 AI 接口调用经验，曾完成聊天机器人项目实践。

三、为什么这样修改
这样的表达更突出技能与项目实践，同时不新增用户未提供的事实。
```

### 失败响应

在流式响应开始前，如果参数错误或 AI 调用失败，后端会返回 JSON 错误，格式与 `POST /polish-resume-json` 基本一致。

示例，简历内容为空，状态码：`400`

```json
{
  "detail": "简历内容不能为空，请填写原始简历内容。"
}
```

示例，AI 服务调用失败，状态码：`502`

```json
{
  "detail": "AI 服务调用失败，请稍后重试。"
}
```

如果流式响应已经开始后连接中断，前端可能收到一段文本提示：

```text
AI 服务连接中断，请稍后重试。
```

## 安全注意事项

- 不要在前端代码中写真实 API Key。
- 不要把真实 API Key 写进本文档。
- 不要提交 `.env` 文件。
- 前端只调用本项目后端接口，不直接调用智谱 AI。
- 后端通过 `ZHIPUAI_API_KEY` 环境变量读取 API Key。
