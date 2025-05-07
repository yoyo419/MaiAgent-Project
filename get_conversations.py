import time
import requests
import requests_cache
from typing import List, Dict, Any, Optional
from config import API_BASE_URL, HEADERS
import logging

# 設置 Cache，避免重複請求
requests_cache.install_cache('api_cache', expire_after=3600)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_conversations(url: str) -> List[Dict[str, Any]]:
    all_messages = []
    with requests.Session() as session:
        while url:
            response = session.get(url, headers=HEADERS, timeout=30)
            if response.status_code != 200:
                print(f"請求失敗，狀態碼: {response.status_code}")
                break
            data = response.json()
            all_messages.extend(data["results"])
            url = data.get("next")
            time.sleep(1)
    return all_messages

def parse_conversations(results: List[Dict[str, Any]], output_file: str, mode: str = 'w') -> None:
    if not results:
        print("回應資料無效或未包含對話結果")
        return
    outgoing_messages = [msg for msg in results if msg.get("type") == "outgoing"]
    sorted_messages = sorted(outgoing_messages, key=lambda x: int(x.get('createdAt', '0')))
    with open(output_file, mode, encoding="utf-8-sig") as file:
        for conversation in sorted_messages:
            file.write(conversation.get('content', '無內容'))
    print(f"對話結果已寫入 `{output_file}`")

def get_replies(conversation_id: str, output_file: str, mode: str = 'w') -> None:
    initial_url = f"{API_BASE_URL}messages/?conversation={conversation_id}"
    conversations = get_conversations(initial_url)
    if conversations:
        parse_conversations(conversations, output_file, mode)
    else:
        print("無法取得對話列表。")
