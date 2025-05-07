import os
import shutil

def copy_doc_files(source_dir, destination_dir):
    # 支援的檔案格式
    doc_extensions = ['.doc', '.docx', '.DOC', '.DOCX']

    for root, dirs, files in os.walk(source_dir):
        # 計算目標資料夾的對應路徑
        relative_path = os.path.relpath(root, source_dir)
        dest_path = os.path.join(destination_dir, relative_path)

        # 建立對應的資料夾結構（若不存在）
        os.makedirs(dest_path, exist_ok=True)

        # 複製符合條件的檔案
        for file in files:
            if any(file.endswith(ext) for ext in doc_extensions):
                source_file_path = os.path.join(root, file)
                dest_file_path = os.path.join(dest_path, file)
                shutil.copy2(source_file_path, dest_file_path)
                print(f"已複製: {source_file_path} -> {dest_file_path}")

# 指定來源和目標資料夾
doc_source = input("請輸入來源資料夾路徑: ")
doc_destination = input("請輸入目標資料夾路徑: ")

copy_doc_files(doc_source, doc_destination)
print("檔案複製完成！")
