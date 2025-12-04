import os
import pandas as pd
import random
from caption_generator import BLIPCaptionGenerator
from retrieval_model import CLIPRetriever

# ================= CẤU HÌNH =================
IMAGE_DIR = r'C:\Users\tungd\OneDrive\Máy tính\Dataset PC Image Parts\pc_parts' 

# Tên file CSV dữ liệu
CAPTION_CSV = 'pc_parts.csv'
query_image_path = r'C:\Users\tungd\OneDrive\Máy tính\hinhanh\Mouse-Tester.jpg'
# ============================================
def main():
    print("=== BẮT ĐẦU CHƯƠNG TRÌNH AI SEARCH ===")

    # ---------------------------------------------------------
    # GIAI ĐOẠN 1: KIỂM TRA DỮ LIỆU & SINH CAPTION (BLIP)
    # ---------------------------------------------------------
    if os.path.exists(CAPTION_CSV):
        print(f"Đã tìm thấy file dữ liệu: {CAPTION_CSV}")
        try:
            df = pd.read_csv(CAPTION_CSV)
            print(f"Số lượng sản phẩm trong CSV: {len(df)}")
            if len(df) == 0:
                print("File CSV rỗng! Đang tiến hành quét lại...")
                raise ValueError("CSV Empty")
        except Exception:
            # Nếu CSV lỗi hoặc rỗng, chạy lại BLIP
            os.remove(CAPTION_CSV)
            blip_gen = BLIPCaptionGenerator()
            blip_gen.generate_captions_for_directory(IMAGE_DIR, CAPTION_CSV)
            df = pd.read_csv(CAPTION_CSV)
    else:
        print("Chưa có dữ liệu, đang chạy BLIP để quét ảnh và tạo chú thích...")
        try:
            blip_gen = BLIPCaptionGenerator()
            blip_gen.generate_captions_for_directory(IMAGE_DIR, CAPTION_CSV)
            df = pd.read_csv(CAPTION_CSV)
        except Exception as e:
            print(f"Lỗi nghiêm trọng Giai đoạn 1: {e}")
            return

    # ---------------------------------------------------------
    # GIAI ĐOẠN 2: KHỞI TẠO VÀ TÌM KIẾM (CLIP)
    # ---------------------------------------------------------
    print("\n=== ĐANG KHỞI TẠO MÔ HÌNH TÌM KIẾM (CLIP/RESNET) ===")
    
    # 1. Khởi tạo model
    try:
        retriever = CLIPRetriever(model_name="RN50", pretrained_name="openai")
    except Exception as e:
        print(f"Lỗi khởi tạo CLIP: {e}")
        return
    
    # 2. Tạo Vector Database (Nạp dữ liệu từ CSV vào RAM)
    retriever.create_product_embeddings(df)
    query_image_path = r'C:\Users\tungd\OneDrive\Máy tính\hinhanh\Mouse-Tester.jpg'
    
    if not df.empty:
        # Lấy ngẫu nhiên 1 dòng trong CSV
        random_row = df.sample(1).iloc[0]
        # Lấy đường dẫn ảnh từ dòng đó
        path_from_csv = random_row['image_path_full']
        
        if os.path.exists(path_from_csv):
            query_image_path = path_from_csv
            print(f"\n Đã chọn ngẫu nhiên 1 ảnh từ dataset để test:")
            print(f"   --> {query_image_path}")
        else:
            print(f"Ảnh trong CSV không tồn tại trên ổ cứng: {path_from_csv}")
    
    #
    if not query_image_path:
        print("Không lấy được ảnh mẫu từ CSV. Vui lòng kiểm tra lại dataset.")
        return

    # 3. Thực hiện tìm kiếm
    print(f"\nĐang tìm kiếm các sản phẩm tương tự...")
    results = retriever.find_similar_products(query_image_path, top_k=5)
    
    print("\n" + "="*50)
    print("           KẾT QUẢ TÌM KIẾM TOP 5")
    print("="*50)
    
    if results:
        for idx, item in enumerate(results):
            info = item['info']
            score = item['score']
            print(f"\nTop {idx+1} (Độ trùng khớp: {score:.4f})")
            print(f"   - Sản phẩm: {info.get('image_name', 'Unknown')}")
            print(f"   - Loại: {info.get('category', 'Unknown')}")
            print(f"   - Mô tả AI: {info.get('caption_auto', 'No caption')}")
            # print(f"   - Đường dẫn: {info.get('image_path_full')}") 
    else:
        print("Không tìm thấy kết quả nào.")

if __name__ == "__main__":
    main()