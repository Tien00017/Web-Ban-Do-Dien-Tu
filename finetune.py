import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import open_clip
import pandas as pd
from PIL import Image
from tqdm import tqdm
import os

# --- CẤU HÌNH ---
CSV_FILE = 'pc_parts_captions_blip.csv'  # File CSV bạn đã tạo
MODEL_NAME = 'RN50'                      # Dùng ResNet50
PRETRAINED = 'openai'
BATCH_SIZE = 16                          # Giảm xuống nếu tràn VRAM (Out of Memory)
EPOCHS = 5                               # Số lần học lặp lại toàn bộ dataset
LEARNING_RATE = 1e-5                     # Tốc độ học thấp để không làm hỏng kiến thức cũ
SAVE_PATH = 'finetuned_clip.pt'          # Nơi lưu model sau khi train
# ----------------

class PCPartsDataset(Dataset):
    def __init__(self, csv_file, preprocess, tokenizer):
        self.data = pd.read_csv(csv_file)
        self.preprocess = preprocess
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        image_path = row['image_path_full']
        caption = str(row['caption_auto'])

        # Xử lý ảnh
        try:
            image = Image.open(image_path).convert("RGB")
            image_tensor = self.preprocess(image)
        except Exception:
            # Nếu lỗi ảnh, tạo ảnh đen để không crash (cách xử lý tạm thời)
            image_tensor = torch.zeros((3, 224, 224))
        
        # Xử lý văn bản (Tokenize)
        text_tokens = self.tokenizer([caption])[0]  # Lấy phần tử đầu tiên

        return image_tensor, text_tokens

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🚀 Bắt đầu Finetuning trên thiết bị: {device}")

    # 1. Tải Model và các công cụ hỗ trợ
    model, _, preprocess = open_clip.create_model_and_transforms(MODEL_NAME, pretrained=PRETRAINED, device=device)
    tokenizer = open_clip.get_tokenizer(MODEL_NAME)

    # Nếu muốn finetune toàn bộ, ta không đóng băng (freeze) lớp nào cả.
    # Nhưng để tiết kiệm bộ nhớ, đôi khi người ta khóa Image Encoder, chỉ train Text Encoder hoặc ngược lại.
    # Ở đây ta train cả hai (Full Finetuning).

    # 2. Chuẩn bị Dữ liệu
    if not os.path.exists(CSV_FILE):
        print("❌ Không tìm thấy file CSV. Hãy chạy main.py trước để tạo dữ liệu."); return

    dataset = PCPartsDataset(CSV_FILE, preprocess, tokenizer)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)

    # 3. Thiết lập Optimizer và Loss
    loss_img = nn.CrossEntropyLoss()
    loss_txt = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)

    # 4. Vòng lặp Huấn luyện (Training Loop)
    for epoch in range(EPOCHS):
        model.train() # Chuyển sang chế độ train
        total_loss = 0
        pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{EPOCHS}")

        for batch in pbar:
            optimizer.zero_grad()
            
            images, texts = batch
            images = images.to(device)
            texts = texts.to(device)

            # Forward pass (Tính toán)
            # Model trả về đặc trưng ảnh và văn bản, cùng với logit_scale
            image_features, text_features, logit_scale = model(images, texts)
            
            # Tính toán ma trận tương đồng (Similarity Matrix)
            logit_scale = logit_scale.exp()
            logits_per_image = logit_scale * image_features @ text_features.t()
            logits_per_text = logits_per_image.t()

            # Tạo nhãn (Labels): Đường chéo của ma trận là cặp đúng (0, 1, 2...)
            ground_truth = torch.arange(len(images), dtype=torch.long, device=device)

            # Tính Loss tổng hợp (Symmetric Loss)
            loss = (loss_img(logits_per_image, ground_truth) + loss_txt(logits_per_text, ground_truth)) / 2

            # Backward pass (Cập nhật trọng số)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            pbar.set_postfix({"Loss": f"{loss.item():.4f}"})

        avg_loss = total_loss / len(dataloader)
        print(f"✅ Kết thúc Epoch {epoch+1}, Loss trung bình: {avg_loss:.4f}")

    # 5. Lưu Model
    print(f"💾 Đang lưu model vào {SAVE_PATH}...")
    torch.save(model.state_dict(), SAVE_PATH)
    print("🎉 Finetuning hoàn tất!")

if __name__ == "__main__":
    main()