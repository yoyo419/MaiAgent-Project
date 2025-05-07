import os
from typing import Optional, Dict, Any
from utils.maiagent import MaiAgentHelper
from config import WEB_CHAT_ID, API_KEY, API_BASE_URL, STORAGE_URL, CHATBOT_ID
import logging

class MessageHandler:
    """統一的訊息處理類別，處理對話創建、圖片上傳和訊息發送"""
    
    def __init__(self):
        """初始化訊息處理類別"""
        self.helper = MaiAgentHelper(
            api_key=API_KEY,
            base_url=API_BASE_URL,
            storage_url=STORAGE_URL
        )
        self.web_chat_id = WEB_CHAT_ID
        self.folder_batch_info = {}
        
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
        """上傳圖片並發送訊息"""
        if not conversation_id:
            logging.error("無效的 conversation_id")
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
                return message_response
            else:
                logging.error(f"訊息發送失敗")
                return None
                
        except Exception as e:
            logging.error(f"上傳和發送過程中發生錯誤：{str(e)}")
            return None
    
    def get_conversation_content(self, conversation_id: str, folder_name: str, batch_num: int = 1,
        total_batches: int = 1) -> None:
        """獲取對話內容並儲存"""
        try:
            if not conversation_id:
                logging.error("無效的對話ID")
                return
                
            # 初始化資料夾的批次資訊
            if folder_name not in self.folder_batch_info:
                self.folder_batch_info[folder_name] = {
                    'total_batches': total_batches,
                    'current_batch': 0
                }
                
            self.folder_batch_info[folder_name]['current_batch'] = batch_num
            
            # 在 output 資料夾中建立輸出檔案
            output_file = os.path.join(self.output_dir, f"{folder_name}.txt")
            
            logging.info(f"儲存對話內容到：{output_file}")
            
            # 如果是同一個資料夾的後續批次，使用附加模式
            mode = 'a' if batch_num > 1 else 'w'
            
            if mode == 'a':
                # 在新批次前加入分隔線
                with open(output_file, 'a', encoding='utf-8-sig') as f:
                    f.write("\n" + "=" * 50 + f"\n批次 {batch_num}/{total_batches}\n" + "=" * 50 + "\n\n")
            
            from get_conversations import get_replies
            get_replies(conversation_id, output_file, mode)
            
            # 檢查是否所有批次都已完成
            if batch_num == total_batches:
                logging.info(f"\n{folder_name} 的所有 {total_batches} 個批次處理完成")
                try:
                    self.upload_knowledge_file(output_file)
                    logging.info("知識庫上傳完成")
                    # 清理該資料夾的批次資訊
                    del self.folder_batch_info[folder_name]
                except Exception as e:
                    logging.error(f"上傳知識庫時發生錯誤：{str(e)}")
                    
        except Exception as e:
            logging.error(f"獲取對話內容時發生錯誤：{str(e)}")
    
    def upload_knowledge_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """上傳知識庫文件"""
        try:
            # 檢查檔案是否存在
            if not os.path.exists(file_path):
                logging.error(f"錯誤：找不到檔案 {file_path}")
                return None
                
            logging.info(f"正在上傳檔案：{file_path}")
            response = self.helper.upload_knowledge_file(CHATBOT_ID, file_path)
            logging.info(f"上傳回應：{response}")
            return response
            
        except Exception as e:
            logging.error(f"上傳過程中發生錯誤：{str(e)}")
            return None 