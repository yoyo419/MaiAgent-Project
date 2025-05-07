import os


def count_pdfs_in_folder(folder_path):
    pdf_count = 0
    # 使用 os.walk 來遞迴掃描資料夾及其子資料夾
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            # 檢查檔案副檔名是否為 .pdf（忽略大小寫）
            if file_name.lower().endswith(".pdf"):
                pdf_count += 1
    return pdf_count


if __name__ == "__main__":
    # 請將此路徑換成你想要掃描的資料夾路徑
    folder_path = "C:/Users/user/Desktop/中經院計劃案/研究計畫下載檔"

    total_pdfs = count_pdfs_in_folder(folder_path)
    print(f"總共有 {total_pdfs} 個 PDF 檔。")
