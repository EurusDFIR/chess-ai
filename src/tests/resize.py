from PIL import Image
import os

image_dir = "R:/TDMU/KIEN_THUC_TDMU/3_year_HK2/TriTueNT/chess-ai/src/gui/assets/pieces/" # Thay đường dẫn thư mục ảnh của bạn

for filename in os.listdir(image_dir):
    if filename.endswith(".png"):
        filepath = os.path.join(image_dir, filename)
        img = Image.open(filepath)
        img_resized = img.resize((64, 64)) # Resize về 64x64
        img_resized.save(filepath) # Ghi đè file gốc (hoặc lưu file mới)
        print(f"Đã resize ảnh: {filename}")

print("Hoàn tất resize ảnh.")