import os
import time
import re
from typing import List, Dict, Any
import logging
from messaging import MessageHandler



def sort_by_page_number(file_name: str) -> int:
    """
    根據檔案名稱中的頁碼進行排序
    支援格式：'page001.jpg'、'1.jpg'、'p1.jpg' 等
    """
    try:
        # 尋找檔名中的數字
        numbers = re.findall(r'\d+', file_name)
        if numbers:
            # 使用最後一個數字作為頁碼
            return int(numbers[-1])
        return float('inf')  # 如果沒有數字，放到最後
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
                if os.path.getsize(full_path) > 0:  # 確保檔案不是空的
                    image_files.append(full_path)

    # 按頁碼排序
    sorted_files = sorted(image_files, key=lambda x: sort_by_page_number(os.path.basename(x)))

    # 輸出排序結果供確認
    print("\n檔案處理順序：")
    for idx, file in enumerate(sorted_files, 1):
        page_num = sort_by_page_number(os.path.basename(file))
        print(f"{idx}. 第 {page_num} 頁: {os.path.basename(file)}")
    print()

    return sorted_files


def process_images_in_conversation(directory: str, message_handler: MessageHandler, batch_size: int = 200) -> Dict[str, Any]:
    """批量處理資料夾內的所有圖片"""
    try:
        folder_name = os.path.basename(directory)
        logging.info(f"\n開始處理資料夾: {folder_name}")

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

    except Exception as e:
        logging.error(f"處理目錄 {directory} 時發生錯誤：{str(e)}", exc_info=True)
        return {}


def process_all_directories(base_directory: str, helper: Any) -> None:
    """遞迴處理所有包含圖片的資料夾"""
    for root, dirs, files in os.walk(base_directory):
        # 檢查當前資料夾是否包含圖片
        has_images = any(file.lower().endswith(('.png', '.jpg', '.jpeg')) for file in files)
        if has_images:
            print(f"\n開始處理資料夾: {root}")
            process_images_in_conversation(root, helper)

# 在日誌配置部分添加時間格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)