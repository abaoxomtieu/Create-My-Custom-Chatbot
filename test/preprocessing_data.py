from docx import Document

def extract_chunks_from_docx_fixed(path_to_docx):
    doc = Document(path_to_docx)
    chunks = []
    current_text = []
    current_images = []
    image_counter = 0

    for para in doc.paragraphs:
        para_has_image = False
        for run in para.runs:
            # Dùng local-name để tìm ảnh
            pics = run._element.xpath(".//*[local-name()='pic']")
            if pics:
                para_has_image = True
                break
        
        if para_has_image:
            # Lưu chunk text trước đó
            if current_text or current_images:
                chunks.append({
                    "content": "\n".join(current_text).strip(),
                    "image_url": current_images.copy()
                })
                current_text = []
                current_images = []

            image_counter += 1
            url = "url" + str(image_counter)
            chunks.append({
                "content": "",
                "image_url": [url]
            })
        else:
            current_text.append(para.text)
    
    # Thêm chunk cuối cùng
    if current_text or current_images:
        chunks.append({
            "content": "\n".join(current_text).strip(),
            "image_url": current_images.copy()
        })

    return chunks


# Thay bằng đường dẫn file Word thực tế của bạn
path = "./Data/Cẩm nang copy 2.docx"
result_chunks = extract_chunks_from_docx_fixed(path)

from pprint import pprint
pprint(result_chunks)
