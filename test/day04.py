import os
import json
from dotenv import load_dotenv
from zai import ZhipuAiClient
from pathlib import Path
from fastapi import  FastAPI,HTTPException
from pydantic import BaseModel


env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("ZHIPUAI_API_KEY")

if not api_key:
    raise ValueError("没有找到api，请检查.env文件")
client = ZhipuAiClient(api_key=api_key)

app = FastAPI()

class ResumeRequest(BaseModel):
    job_target: str
    resume_text: str

class ResumeJsonResponse(BaseModel):
    problem_analysis: list[str]
    optimized_resume: str
    reasons: list[str]

def clean_json_text(text:str)->str:
    text = text.strip()
    if text.startswith("```json"):
        text = text.removeprefix("```json").strip()
    if text.startswith("```"):
        text = text.removeprefix("```").strip()
    if text.endswith("```"):
        text = text.removeprefix("```").strip()
    return text

def ask_ai(resume_text: str, job_target: str) -> ResumeJsonResponse:
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
3. 如果原文只说“Python、AI接口、聊天机器人”，就只能围绕这些内容优化
4. 可以让表达更专业，但不能把没有做过的事情写进去

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
    content = response.choices[0].message.content
    try:
        json_text = clean_json_text(content)
        data = json.loads(json_text)
        return ResumeJsonResponse(
            problem_analysis=data["problem_analysis"],
            optimized_resume=data["optimized_resume"],
            reasons = data["reasons"]
        )
    except Exception as e:
        raise  HTTPException(
            status_code = 500,
            detail=f"AI 返回内容不是合法 JSON。原始内容：{content}"
        )


@app.get("/")
def home():
    return {"message": "AI 简历润色助手 API 已启动"}
@app.post("/polish-resume-json",response_model=ResumeJsonResponse)
def polish_resume_apo(request:ResumeRequest):
    return  ask_ai(
        resume_text = request.resume_text,
        job_target = request.job_target
    )



'''if __name__ == "__main__":
    job_target = input("请输入你的目标岗位:")
    resume_text = input("请输入你简历的内容：")
    print("\nAI正在优化你的简历，请稍等...")
    result = ask_ai(resume_text,job_target)
    print("\nAI回答:")
    print(result)
'''