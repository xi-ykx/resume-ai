import os
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录和运行时数据路径。
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
DATA_DIR = BASE_DIR / "data"
HISTORY_PATH = DATA_DIR / "history.json"

# 加载本地环境变量，不打印 .env 内容。
load_dotenv(dotenv_path=ENV_PATH)

# DeepSeek API 配置。
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-flash"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    raise ValueError("没有找到 DeepSeek API Key，请检查 .env 文件")

# 输入长度限制。
MAX_JOB_TARGET_LENGTH = 100
MAX_RESUME_TEXT_LENGTH = 8000

# 本地开发允许的来源。包含 "null" 是因为通过 file:// 协议直接打开
# index.html 时浏览器会发送 Origin: null。生产环境请移除此项。
LOCAL_ALLOWED_ORIGINS = [
    "null",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "http://localhost:5500"
]
LOCAL_CLIENT_HOSTS = {"127.0.0.1", "::1", "localhost"}

# 本地历史记录访问令牌，前端需要在请求头中携带。
LOCAL_HISTORY_TOKEN = "local-dev-history-token"
