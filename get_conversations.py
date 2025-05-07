import time
import requests
from typing import List, Dict, Any, Optional
from config import API_BASE_URL, HEADERS
import logging
import datetime  # 添加這行來導入日期時間模組

# 在日誌配置部分添加時間格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_conversations(url: str) -> List[Dict[str, Any]]:
    """
    從 API 獲取對話列表並返回所有訊息
    """
    all_messages = []  # 存放所有訊息的列表

    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"請求失敗，狀態碼: {response.status_code}")
            break

        data = response.json()
        all_messages.extend(data["results"])  # 累積結果
        url = data.get("next")  # 更新為下一個請求的 URL
        time.sleep(1)  # 避免請求過於頻繁

    return all_messages


def parse_conversations(results: List[Dict[str, Any]], output_file: str, mode: str = 'w') -> None:
    """
    解析對話回應並依照時間順序寫入檔案
    mode: 'w' 為覆寫模式，'a' 為附加模式
    """
    if not results:
        print("回應資料無效或未包含對話結果")
        return

    # 只處理外發訊息
    outgoing_messages = [msg for msg in results if msg.get("type") == "outgoing"]

    # 根據 createdAt 時間戳記排序訊息（從舊到新）
    sorted_messages = sorted(outgoing_messages, key=lambda x: int(x.get('createdAt', '0')))

    # 寫入排序後的訊息
    with open(output_file, mode, encoding="utf-8-sig") as file:
        for conversation in sorted_messages:
            file.write(conversation.get('content', '無內容'))

    print(f"對話結果已寫入 `{output_file}`")


def get_replies(conversation_id: str, output_file: str, mode: str = 'w') -> None:
    """
    獲取對話回覆並寫入檔案
    conversation_id: 對話 ID
    output_file: 輸出檔案路徑
    mode: 'w' 為覆寫模式，'a' 為附加模式
    """
    initial_url = f"{API_BASE_URL}messages/?conversation={conversation_id}"
    conversations = get_conversations(initial_url)

    if conversations:
        parse_conversations(conversations, output_file, mode)
    else:
        print("無法取得對話列表。")