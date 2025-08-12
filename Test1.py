import fitz  # PyMuPDF
from PIL import Image
import os


def pdf_to_images_pymupdf(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    try:
        doc = fitz.open(pdf_path)

        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(dpi=300)

            png_path = os.path.join(output_folder, f"{pdf_name}_page_{i + 1}.png")
            pix.save(png_path)
            print(f"已保存: {png_path}")

            # 如果需要 JPG，可以从 PNG 转换
            img = Image.open(png_path)
            jpg_path = os.path.join(output_folder, f"{pdf_name}_page_{i + 1}.jpg")
            img.save(jpg_path, "JPEG", quality=95)
            print(f"已保存: {jpg_path}")

        return True
    except Exception as e:
        print(f"转换过程中发生错误: {e}")
        return False


if __name__ == "__main__":
    pdf_file = r"C:\Users\吴永恒\Downloads\【协助灵积客户】通义千问大模型API接口合作协议1.pdf"
    output_dir = r"C:\Users\吴永恒\Downloads\pdf_images"

    pdf_to_images_pymupdf(pdf_file, output_dir)
