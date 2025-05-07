import os
import time
import re
import logging
import markitdown
from typing import List, Dict, Any
from messaging import MessageHandler
from get_conversations import get_replies  
from config import API_BASE_URL  
from utils import MaiAgentHelper
from 轉檔 import file_path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


# 初始化 MessageHandler
message_handler = MessageHandler()

def convert_doc_to_markdown(doc_path):
    """
    使用 markitdown 轉換 .doc 檔案為 Markdown。
    """
    try:
        md_content = markitdown.convert(doc_path)  # 透過 markitdown 轉換
        md_path = doc_path.replace(".doc", ".md")

        with open(md_path, "w", encoding="utf-8") as md_file:
            md_file.write(md_content)

        logging.info(f" 轉換完成：{doc_path} -> {md_path}")
        return md_path
    except Exception as e:
        logging.error(f" 轉換失敗 {doc_path}：{e}")
        return None



def sort_by_page_number(file_name: str) -> int:
    """根據檔案名稱中的頁碼進行排序"""
    try:
        numbers = re.findall(r'\d+', file_name)
        if numbers:
            return int(numbers[-1])
        return float('inf')
    except Exception as e:
        logging.warning(f"解析檔案名稱 '{file_name}' 時發生錯誤：{str(e)}")
        return float('inf')

def get_all_images(directory: str) -> List[str]:
    """遞迴獲取所有圖片檔案並按頁碼排序"""
    image_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                full_path = os.path.join(root, file)
                try:
                    if os.path.getsize(full_path) > 0:
                        image_files.append(full_path)
                except OSError as e:
                    logging.warning(f"無法讀取檔案大小: {full_path}, 錯誤: {str(e)}")
    sorted_files = sorted(image_files, key=lambda x: sort_by_page_number(os.path.basename(x)))
    return sorted_files

def upload_images_batch(session, images: List[str], url: str) -> None:
    """批次上傳圖片"""
    files = [("file", open(image, "rb")) for image in images]
    for attempt in range(3):
        try:
            response = session.post(url, files=files, timeout=60)
            if response.status_code == 200:
                logging.info("批次上傳成功！")
                break
            else:
                logging.error(f"批次上傳失敗，狀態碼: {response.status_code}，重試中...")
                time.sleep(5)
        except Exception as e:
            logging.error(f"上傳過程中發生錯誤: {str(e)}，重試中...")
            time.sleep(5)

def process_images_in_conversation(directory: str, message_handler: MessageHandler, batch_size: int = 200) -> Dict[str, Any]:
    """批量處理資料夾內的所有圖片"""
    folder_name = os.path.basename(directory)
    logging.info(f"開始處理資料夾: {folder_name}")
    image_files = get_all_images(directory)

    if not image_files:
        logging.warning(f"目錄 {directory} 中沒有找到有效的圖片")
        # 獲取按頁碼排序的圖片列表
        image_files = get_all_images(directory)

        if not image_files:
            logging.warning(f"目錄 {directory} 中沒有找到有效的圖片")
            return {}

        results = {}
        total_images = len(image_files)
        total_batches = (total_images + batch_size - 1) // batch_size

        logging.info(f"找到 {total_images} 張圖片，將分成 {total_batches} 個批次處理")

        for batch_num in range(total_batches):
            try:
                conversation_id = message_handler.create_conversation()
                if not conversation_id:
                    logging.error(f"批次 {batch_num + 1} 建立對話失敗，跳過此批次")
                    continue

                logging.info(f"\n開始處理批次 {batch_num + 1}/{total_batches}, 對話ID: {conversation_id}")

                # 處理當前批次的圖片
                start_idx = batch_num * batch_size
                end_idx = min((batch_num + 1) * batch_size, total_images)
                current_batch = image_files[start_idx:end_idx]

                for idx, image_path in enumerate(current_batch, 1):
                    page_num = sort_by_page_number(os.path.basename(image_path))
                    logging.info(f"[{idx}/{len(current_batch)}] 處理第 {page_num} 頁：{os.path.basename(image_path)}")

                    response = message_handler.upload_and_send(conversation_id, image_path)
                    if response:
                        results[image_path] = response
                        logging.info("✓ 處理成功")
                    else:
                        results[image_path] = "失敗"
                        logging.error("✗ 處理失敗")

                    time.sleep(10)

                # 儲存對話內容
                logging.info(f"正在儲存批次 {batch_num + 1} 的對話內容...")
                message_handler.get_conversation_content(
                    conversation_id=conversation_id,
                    folder_name=folder_name,
                    batch_num=batch_num + 1,
                    total_batches=total_batches
                )
                logging.info(f"批次 {batch_num + 1} 完成")

            except Exception as e:
                logging.error(f"處理批次 {batch_num + 1} 時發生錯誤：{str(e)}", exc_info=True)
                continue

        return results


    total_images = len(image_files)
    total_batches = (total_images + batch_size - 1) // batch_size
    logging.info(f"找到 {total_images} 張圖片，將分成 {total_batches} 個批次處理")

    for batch_num in range(total_batches):
        try:
            conversation_id = message_handler.create_conversation()
            if not conversation_id:
                logging.error(f"批次 {batch_num + 1} 建立對話失敗，跳過此批次")
                continue

            logging.info(f"開始處理批次 {batch_num + 1}/{total_batches}, 對話ID: {conversation_id}")

            # 處理當前批次的圖片
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, total_images)
            current_batch = image_files[start_idx:end_idx]

            with message_handler.session as session:  # 統一使用 session
                upload_images_batch(session, current_batch, API_BASE_URL)
            time.sleep(2)

            
            logging.info(f"正在儲存批次 {batch_num + 1} 的對話內容...")
            get_replies(conversation_id, f"output/{folder_name}.txt", mode='a')
            logging.info(f"批次 {batch_num + 1} 完成")

        except Exception as e:
            logging.error(f"處理批次 {batch_num + 1} 時發生錯誤：{str(e)}", exc_info=True)
            continue

    logging.info("所有圖片已完成上傳！")
    return results

def process_all_directories(base_directory: str, message_handler: MessageHandler) -> None:
    """遞迴處理所有包含圖片和 .doc 檔案的資料夾"""
    for root, dirs, files in os.walk(base_directory):
        has_images = any(file.lower().endswith(('.png', '.jpg', '.jpeg')) for file in files)
        has_docs = any(file.lower().endswith('.doc') for file in files)

        # 如果資料夾包含圖片，處理圖片
        if has_images:
            logging.info(f" 開始處理圖片資料夾: {root}")
            process_images_in_conversation(root, message_handler)

        # 如果資料夾包含 .doc，轉換為 .md
        if has_docs:
            for file in files:
                file_path = os.path.join(root, file)
                logging.info(f" 轉換 {file} 為 Markdown...")
                convert_doc_to_markdown(file_path)

