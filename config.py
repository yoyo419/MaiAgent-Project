import os
import logging
from dotenv import load_dotenv, find_dotenv

# 嘗試載入環境變數
env_path = find_dotenv()
load_dotenv(env_path, override=True)


API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")
WEB_CHAT_ID = os.getenv("WEB_CHAT_ID")
CHATBOT_ID = os.getenv("CHATBOT_ID")
STORAGE_URL = os.getenv("STORAGE_URL")

print(f"API_BASE_URL: {API_BASE_URL}")
print(f"API_KEY: {API_KEY}")
print(f"WEB_CHAT_ID: {WEB_CHAT_ID}")
print(f"CHATBOT_ID: {CHATBOT_ID}")
print(f"STORAGE_URL: {STORAGE_URL}")

# 設定 HTTP 標頭
HEADERS = {
    "Authorization": f'Api-Key {API_KEY}'
}

# 日誌配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)