import os
import time
import re
import logging
import requests
from typing import Optional, Dict, Any
from utils.maiagent import MaiAgentHelper
from config import WEB_CHAT_ID, API_KEY, API_BASE_URL, STORAGE_URL, CHATBOT_ID
from get_conversations import get_replies

# 日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

LOG_FILE = "processed_images.txt"  # 已處理圖片記錄檔案
RETRY_COUNT = 3  # 上傳失敗最多重試次數

def load_processed_images():
    """讀取已處理的圖片列表"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()

def save_processed_image(image_path):
    """將成功處理的圖片記錄到檔案"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(image_path + "\n")

class MessageHandler:
    """統一的訊息處理類別，處理對話創建、圖片上傳和訊息發送"""
    
    def __init__(self):
        self.helper = MaiAgentHelper(
            api_key=API_KEY,
            base_url=API_BASE_URL,
            storage_url=STORAGE_URL
        )
        self.web_chat_id = WEB_CHAT_ID
        self.folder_batch_info = {}
        self.session = requests.Session()

        # 建立 output 資料夾
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def create_conversation(self):
        """建立新對話並返回對話ID"""
        try:
            response = self.helper.create_conversation(self.web_chat_id)
            conversation_id = response.get("id")
            if conversation_id:
                logging.info(f"成功建立對話，Conversation ID：{conversation_id}")
            else:
                logging.error("建立對話失敗，無法取得 Conversation ID。")
            return conversation_id
        except Exception as e:
            logging.error(f"建立對話時發生錯誤：{str(e)}")
            return None
    
    def upload_and_send(self, conversation_id: str, image_path: str) -> Optional[Dict[str, Any]]:
        """上傳圖片並發送訊息，支援續傳"""
        if not conversation_id:
            logging.error("無效的 conversation_id")
            return None

        # 續傳
        processed_images = load_processed_images()
        if image_path in processed_images:
            logging.info(f" {image_path} 已上傳過，跳過處理")
            return None

        try:
            if not os.path.exists(image_path):
                logging.error(f"檔案不存在：{image_path}")
                return None

            logging.info(f"正在上傳檔案：{image_path}")
            upload_response = self.helper.upload_attachment(conversation_id, image_path)

            if not upload_response or 'id' not in upload_response:
                logging.error(f"附件上傳失敗：{image_path}")
                return None

            attachment_id = upload_response['id']
            logging.info(f"附件上傳成功，ID：{attachment_id}")

            # 發送訊息
            message_response = self.helper.send_message(
                conversation_id=conversation_id,
                content="",
                attachments=[{
                    'id': attachment_id,
                    'type': 'image',
                    'filename': os.path.basename(image_path),
                    'file': upload_response.get('file', '')
                }]
            )

            if message_response:
                logging.info(f"訊息發送成功")
                save_processed_image(image_path)  # 記錄成功上傳的圖片
                return message_response
            else:
                logging.error(f"訊息發送失敗")
                return None

        except Exception as e:
            logging.error(f"上傳和發送過程中發生錯誤：{str(e)}")
            return None
    
    def get_conversation_content(self, conversation_id: str, folder_name: str, batch_num: int = 1, total_batches: int = 1) -> None:
        """獲取對話內容並儲存"""
        try:
            if not conversation_id:
                logging.error("無效的對話ID")
                return

            output_file = os.path.join(self.output_dir, f"{folder_name}.txt")
            mode = 'a' if batch_num > 1 else 'w'

            get_replies(conversation_id, output_file, mode)

            # 檢查txt檔是否為空
            if os.path.getsize(output_file) == 0:
                logging.warning(f" {output_file} 為空，跳過上傳到知識庫！")
                return

            if batch_num == total_batches:
                logging.info(f"\n{folder_name} 的所有 {total_batches} 個批次處理完成")
                self.upload_knowledge_file(output_file)

        except Exception as e:
            logging.error(f"獲取對話內容時發生錯誤：{str(e)}")
    
    def upload_knowledge_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """上傳知識庫文件，支援重試機制"""
        try:
            if not os.path.exists(file_path):
                logging.error(f"錯誤：找不到檔案 {file_path}")
                return None

            logging.info(f"正在上傳檔案：{file_path}")

            # 失敗重試
            for attempt in range(RETRY_COUNT):
                response = self.helper.upload_knowledge_file(CHATBOT_ID, file_path)
                if response:
                    logging.info(f"知識庫上傳成功: {response}")
                    return response
                else:
                    logging.warning(f"上傳失敗，重試 {attempt + 1}/{RETRY_COUNT}")
                    time.sleep(2)
            
            logging.error(" 知識庫上傳最終失敗！")
            return None

        except Exception as e:
            logging.error(f"上傳過程中發生錯誤：{str(e)}")
            return None
