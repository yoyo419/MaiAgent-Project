import os
import fitz


input_dir = ""
output_dir = ""

if not os.path.exists(input_dir):
    print(f"Input directory does not exist: {input_dir}")
    exit(1)

for root, _, files in os.walk(input_dir):
    for file in files:
        if file.startswith("."):
            continue
        if file.lower().endswith(".pdf"):
            file_path = os.path.join(root, file)
            print(f"Processing: {file_path}")
            try:
                relative_path = os.path.relpath(root, input_dir)
                pdf_name = os.path.splitext(file)[0]
                pdf_output_dir = os.path.join(output_dir, relative_path, pdf_name)
                os.makedirs(pdf_output_dir, exist_ok=True)
                pdf_document = fitz.open(file_path)
                for page_number in range(len(pdf_document)):
                    page = pdf_document.load_page(page_number)
                    pix = page.get_pixmap()
                    output_filename = f"page{page_number + 1}.png"
                    output_path = os.path.join(pdf_output_dir, output_filename)
                    pix.save(output_path)
                    print(f"Saved: {output_path}")
            except Exception as e:
                print(f"Failed to process {file}: {e}")