import os
from http.client import responses
from multiprocessing.connection import answer_challenge

from dotenv import load_dotenv
from zai import ZhipuAiClient
from pathlib import Path

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("ZHIPUAI_API_KEY")

if not api_key:
    raise ValueError("没有找到api，请检查.env文件")
client = ZhipuAiClient(api_key=api_key)

def ask_ai(resume_text:str,job_target:str)->str:
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
    return  response.choices[0].message.content
if __name__ == "__main__":
    job_target = input("请输入你的目标岗位:")
    resume_text = input("请输入你简历的内容：")
    print("\nAI正在优化你的简历，请稍等...")
    result = ask_ai(resume_text,job_target)
    print("\nAI回答:")
    print(result)