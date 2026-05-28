import logging
from typing import Optional

from fastapi import HTTPException
from openai import OpenAI

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

logger = logging.getLogger("ai_resume_optimizer")

# 创建 DeepSeek 客户端，后续所有模型调用都通过这个 client 完成。
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)

# 根据异常类型返回对用户友好的错误，不暴露 API Key 或简历原文。
def raise_ai_call_error(error: Exception) -> None:
    error_name = error.__class__.__name__.lower()

    if "timeout" in error_name:
        logger.error(
            "ai_call_error error_type=%s status_code=504",
            error.__class__.__name__
        )
        raise HTTPException(
            status_code=504,
            detail="AI 服务请求超时，请稍后重试。"
        ) from error

    logger.error(
        "ai_call_error error_type=%s status_code=502",
        error.__class__.__name__
    )
    raise HTTPException(
        status_code=502,
        detail="AI 服务调用失败，请稍后重试。"
    ) from error

# 统一发起 DeepSeek AI 请求，所有调用异常都转换成 JSON 格式的 HTTP 错误。
def create_ai_completion(messages: list[dict], temperature: float, stream: bool = False):
    try:
        return client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            temperature=temperature,
            stream=stream
        )
    except Exception as error:
        raise_ai_call_error(error)

# 安全读取非流式 AI 返回内容，避免返回为空或结构异常时继续处理。
def get_ai_message_content(response) -> str:
    try:
        content = response.choices[0].message.content
    except Exception as error:
        logger.error(
            "ai_response_error error_type=%s status_code=502",
            error.__class__.__name__
        )
        raise HTTPException(
            status_code=502,
            detail="AI 返回结构异常，请稍后重试。"
        ) from error

    if not content or not content.strip():
        logger.error("ai_response_error error_type=EmptyAIContent status_code=502")
        raise HTTPException(
            status_code=502,
            detail="AI 返回内容为空，请稍后重试。"
        )

    return content

# 安全读取流式返回中的文本片段。
def get_ai_stream_content(chunk) -> Optional[str]:
    try:
        return chunk.choices[0].delta.content
    except Exception as error:
        logger.error(
            "ai_stream_error error_type=%s status_code=502",
            error.__class__.__name__
        )
        raise HTTPException(
            status_code=502,
            detail="AI 流式返回结构异常，请稍后重试。"
        ) from error

# 在开始 StreamingResponse 前先拿到第一段内容，便于失败时返回 JSON 错误。
def prepare_ai_stream(response):
    try:
        for chunk in response:
            content = get_ai_stream_content(chunk)
            if content:
                return content, response
    except HTTPException:
        raise
    except Exception as error:
        raise_ai_call_error(error)

    logger.error("ai_stream_error error_type=EmptyAIStreamContent status_code=502")
    raise HTTPException(
        status_code=502,
        detail="AI 返回内容为空，请稍后重试。"
    )

# 继续输出已经通过首段校验的流式内容。
def stream_ai_content(first_content: str, response):
    yield first_content

    try:
        for chunk in response:
            content = get_ai_stream_content(chunk)
            if content:
                yield content
    except Exception as error:
        logger.warning(
            "ai_stream_interrupted error_type=%s",
            error.__class__.__name__
        )
        yield "\n\nAI 服务连接中断，请稍后重试。"
