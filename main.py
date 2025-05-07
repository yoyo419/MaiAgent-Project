import os
import logging
from config import API_KEY, API_BASE_URL, STORAGE_URL
from messaging import MessageHandler
from batch_process import process_all_directories

def main():
    # 設定日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 初始化訊息處理器
    message_handler = MessageHandler()
    
    # 處理指定目錄
    base_directory = input("請輸入要處理的基礎目錄路徑: ")
    if not os.path.exists(base_directory):
        logging.error(f"目錄不存在: {base_directory}")
        return
    
    # 開始處理所有目錄
    process_all_directories(base_directory, message_handler)
    
    logging.info("所有處理完成")

if __name__ == "__main__":
    main()