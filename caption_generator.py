import os
import pandas as pd
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from tqdm import tqdm

class BLIPCaptionGenerator:
    def __init__(self, model_name="Salesforce/blip-image-captioning-base"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"--- Đang tải mô hình BLIP: {model_name} ---")
        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(model_name).to(self.device)
        self.model.eval()
        print("Tải mô hình BLIP hoàn tất.")

    def generate_caption_for_image(self, image_path: str) -> str:
        try:
            raw_image = Image.open(image_path).convert('RGB')
            inputs = self.processor(raw_image, return_tensors="pt").to(self.device)
            out = self.model.generate(**inputs, max_length=50, num_beams=5) 
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            return caption
        except Exception:
            return "ERROR: Caption generation failed."

    def generate_captions_for_directory(self, image_dir: str, output_csv_path: str):
        if not os.path.isdir(image_dir):
            print(f"Thư mục không tồn tại: {image_dir}"); return

        caption_records = []
        print(f"--- Bắt đầu quét ảnh trong: {image_dir} ---")
        
        # Quét đệ quy (Recursive)
        for root, dirs, files in os.walk(image_dir):
            for image_name in tqdm(files, desc=f"Scanning {os.path.basename(root)}"):
                if image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    image_path = os.path.join(root, image_name)
                    caption = self.generate_caption_for_image(image_path)
                    caption_records.append({
                        'image_name': image_name,
                        'category': os.path.basename(root),
                        'image_path_full': image_path,
                        'caption_auto': caption
                    })

        if caption_records:
            df = pd.DataFrame(caption_records)
            df.to_csv(output_csv_path, index=False)
            print(f"\nHoàn tất! Đã lưu CSV tại: {output_csv_path}")
        else:
            print("Không tìm thấy ảnh nào.")