import os
import json
from pathlib import Path
from dotenv import load_dotenv
from zai import ZhipuAiClient
from fastapi import FastAPI,HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field

# 找到当前 day06.py 所在目录下的 .env 文件路径。
env_path = Path(__file__).resolve().parent / '.env'

# 把 .env 里的环境变量加载到当前 Python 进程中。
load_dotenv(dotenv_path=env_path)

# 从环境变量里读取智谱 AI 的 API Key。
api_key = os.getenv("ZHIPUAI_API_KEY")

# 如果没有配置 API Key，程序启动时直接报错，避免后面调用 AI 时才失败。
if not api_key:
    raise ValueError("没有找到api，请检查.env文件")

# 创建智谱 AI 客户端，后续所有模型调用都通过这个 client 完成。
client = ZhipuAiClient(api_key= api_key)

# 创建 FastAPI 应用对象，uvicorn 会加载这个 app 对外提供 Web 服务。
app = FastAPI()

# 配置跨域访问，方便本地 index.html 页面调用 127.0.0.1:8000 的后端接口。
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# 定义前端请求后端时必须提交的数据格式。
class ResumeRequest(BaseModel):
    # 目标岗位至少 2 个字符，例如“AI应用工程师”。
    job_target: str = Field(..., min_length=2, description="目标岗位")

    # 简历内容至少 5 个字符，避免用户提交空内容。
    resume_text: str = Field(..., min_length=5, description="简历内容")

# 定义结构化接口返回给前端的数据格式。
class ResumeJsonResponse(BaseModel):
    # 原始简历存在的问题列表。
    problem_analysis:list[str]

    # 优化后的简历正文。
    optimized_resume:str

    # 解释为什么这样优化。
    reasons:list[str]

# 清理 AI 可能额外包上的 Markdown 代码块，方便后续 json.loads 解析。
def clean_json_text(text: str) -> str:
    # 去掉前后空白字符。
    text = text.strip()

    # 如果 AI 返回了 ```json 开头，就移除这个标记。
    if text.startswith("```json"):
        text = text.removeprefix("```json").strip()

    # 如果 AI 返回了普通代码块 ``` 开头，也移除。
    if text.startswith("```"):
        text = text.removeprefix("```").strip()

    # 如果 AI 返回内容以 ``` 结尾，移除结尾代码块标记。
    if text.endswith("```"):
        text = text.removesuffix("```").strip()

    # 返回清理后的文本，预期应该是纯 JSON 字符串。
    return text

# 普通文本版 AI 调用，主要用于命令行运行 python day06.py 时测试。
def ask_ai(resume_text:str,job_target:str)->str:
    # 调用智谱 AI 的聊天补全接口，请模型按固定三段格式输出文本。
    response = client.chat.completions.create(
        model="glm-5.1",
        messages=[
            {
                "role":"system",
                "content":"""
你是一个专业的简历优化顾问，擅长帮助求职者把普通经历改写成更适合招聘场景的表达。

你的任务：
1. 分析原始简历内容的问题
2. 根据目标岗位优化表达
3. 尽量使用具体、专业、结果导向的语言
4. 不要编造不存在的经历、数据或项目
5. 用中文回答
"""
            },
            {
                "role":"user",
                "content":f"""
目标岗位：{job_target}

原始简历内容：
{resume_text}

请按照下面格式输出：

一、原始内容存在的问题
二、优化后的简历表达
三、为什么这样修改
"""
            }
        ],
        temperature=0.6
    )

    # 取出模型返回的文本内容。
    return  response.choices[0].message.content

# 结构化 JSON 版 AI 调用，供 /polish-resume-json 接口使用。
def ask_ai_json(job_target:str,resume_text:str)->ResumeJsonResponse:
    # 低 temperature 可以让模型输出更稳定，更适合要求严格 JSON 的场景。
    response = client.chat.completions.create(
        model="glm-5.1",
        messages=[
            {
                "role": "system",
                "content": """
    你是一个专业的简历优化顾问。

    你必须严格返回 JSON。
    不要返回 Markdown。
    不要返回解释。
    不要返回代码块。
    不要返回 ```json。
    不要编造不存在的经历、数据或项目。

    重要规则：
    1. 只能基于用户提供的原始简历内容优化表达
    2. 禁止添加用户没有明确提供的技术栈、框架、项目成果、上线经历和量化数据
    3. 可以让表达更专业，但不能新增事实

    返回内容必须可以直接被 Python 的 json.loads() 解析。

    JSON 格式必须严格如下：

    {
      "problem_analysis": ["问题1", "问题2"],
      "optimized_resume": "优化后的简历表达",
      "reasons": ["理由1", "理由2"]
    }
    """
            },
            {
                "role": "user",
                "content": f"""
    目标岗位：{job_target}

    原始简历内容：
    {resume_text}

    请根据目标岗位优化这段简历。
    只返回 JSON，不要返回任何其他文字。
    """
            }
        ],
        temperature=0.1
    )

    # 取出 AI 返回的原始文本，后面会尝试按 JSON 解析。
    content = response.choices[0].message.content

    try:
        # 先清理可能出现的 Markdown 代码块，再解析 JSON。
        json_text = clean_json_text(content)
        data = json.loads(json_text)

        # 用 Pydantic 响应模型重新组织数据，确保返回结构符合接口声明。
        return ResumeJsonResponse(
            problem_analysis=data["problem_analysis"],
            optimized_resume=data["optimized_resume"],
            reasons=data["reasons"]
        )
    except Exception:
        # 如果 AI 没有返回合法 JSON，返回 500 错误给前端。
        raise HTTPException(
            status_code=500,
            detail=f"AI 返回内容不是合法 JSON。原始内容：{content}"
        )


# 流式文本版 AI 调用，供 /polish-resume-stream 接口使用。
def ask_ai_stream(resume_text:str,job_target:str):
    # stream=True 表示模型边生成边返回，前端可以逐步显示内容。
    response = client.chat.completions.create(
        model="glm-5.1",
        messages=[
            {
                "role": "system",
                "content": """
    你是一个专业的简历优化顾问，擅长帮助求职者把普通经历改写成更适合招聘场景的表达。

    规则：
    1. 不要编造用户没有提供的经历、技术栈、项目成果或数据
    2. 可以优化表达，但不能新增事实
    3. 用中文回答
    4. 输出适合人类阅读的简历优化建议
    """
            },
            {
                "role": "user",
                "content": f"""
    目标岗位：{job_target}

    原始简历内容：
    {resume_text}

    请按照下面格式输出：

    一、原始内容存在的问题
    二、优化后的简历表达
    三、为什么这样修改
    """
            }
        ],
        temperature=0.6,
        stream=True
    )

    # 逐个读取模型返回的数据块，把有内容的部分 yield 给 StreamingResponse。
    for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content

# 根路径接口，用来快速确认 API 服务已经启动。
@app.get("/")
def home():
    return {"message": "AI 简历润色助手 API 已启动"}

# 结构化简历优化接口，前端点击“结构化优化简历”时会调用它。
@app.post("/polish-resume-json", response_model=ResumeJsonResponse)
def polish_resume_json_api(request: ResumeRequest):
    # 从请求体中取出简历内容和目标岗位，交给 JSON 版 AI 函数处理。
    return ask_ai_json(
        resume_text=request.resume_text,
        job_target=request.job_target
    )

# 流式简历优化接口，前端点击“流式优化简历”时会调用它。
@app.post("/polish-resume-stream")
def polish_resume_stream_api(request:ResumeRequest):
    # StreamingResponse 会把 ask_ai_stream 生成的文本块持续返回给浏览器。
    return StreamingResponse(
        ask_ai_stream(
            resume_text=request.resume_text,
            job_target=request.job_target
        ),
        media_type = 'text/plain; charset = utf-8'
    )

# 健康检查接口，常用于确认后端进程是否正常。
@app.get('/health')
def health_check():
    return {"status":"ok"}

# 当直接执行 python day06.py 时，进入命令行交互模式；被 uvicorn 导入时不会执行这里。
if __name__ == "__main__":
    # 从命令行读取用户输入。
    job_target = input("请输入你的目标岗位:")
    resume_text = input("请输入你简历的内容：")

    # 调用普通文本版 AI 函数，并把结果打印到终端。
    print("\nAI正在优化你的简历，请稍等...")
    result = ask_ai(resume_text,job_target)
    print("\nAI回答:")
    print(result)
