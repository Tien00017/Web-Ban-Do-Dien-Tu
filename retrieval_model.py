import os
import torch
import numpy as np
import open_clip
import pandas as pd
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

class CLIPRetriever:
    def __init__(self, model_name="RN50", pretrained_name="openai"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"--- Đang tải mô hình CLIP: {model_name} ({pretrained_name}) ---")
        # Tải model CLIP (ResNet50)
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(model_name, pretrained='openai', device=self.device)
        self.model.eval()
        self.product_vectors = None
        self.product_metadata = None
        print("Tải mô hình CLIP hoàn tất.")
    def create_product_embeddings(self, metadata_df: pd.DataFrame):
        """
        Đọc ảnh từ DataFrame và tạo Cơ sở dữ liệu Vector (Offline Step).
        Bao gồm kiểm tra an toàn để tránh lỗi NaN/Inf.
        """
        product_embeddings = []
        product_metadata_list = []
        
        print(f"--- Bắt đầu mã hóa {len(metadata_df)} ảnh sang Vector ---")
        
        # Lặp qua từng dòng trong CSV
        for index, row in tqdm(metadata_df.iterrows(), total=len(metadata_df), desc="Encoding"):
            # Lấy đường dẫn tuyệt đối từ cột 'image_path_full'
            image_path = row.get('image_path_full')
            
            # Kiểm tra đường dẫn có hợp lệ không
            if not image_path or not os.path.exists(image_path):
                continue
                
            try:
                # Mở và tiền xử lý ảnh
                image = Image.open(image_path).convert("RGB")
                image_input = self.preprocess(image).unsqueeze(0).to(self.device)
                
                with torch.no_grad():
                    # Mã hóa ảnh thành vector đặc trưng
                    image_features = self.model.encode_image(image_input)
                    
                    # === BƯỚC KIỂM TRA AN TOÀN (QUAN TRỌNG) ===
                    # 1. Kiểm tra nếu vector chứa NaN (Not a Number) hoặc Inf (Vô cực)
                    if not torch.isfinite(image_features).all():
                        # tqdm.write(f"Vector hỏng (NaN/Inf) tại: {image_path}. Bỏ qua.")
                        continue
                    
                    # 2. Kiểm tra độ dài vector (Norm). Nếu norm = 0 thì không thể chuẩn hóa.
                    norm = image_features.norm(dim=-1, keepdim=True)
                    if norm.item() == 0:
                        # tqdm.write(f"Vector rỗng (Norm=0) tại: {image_path}. Bỏ qua.")
                        continue
                    
                    # 3. Chuẩn hóa L2 an toàn
                    image_features /= norm
                
                # Lưu vector và metadata tương ứng
                product_embeddings.append(image_features.cpu().numpy().flatten())
                product_metadata_list.append(row.to_dict())
                
            except Exception as e:
                # print(f"Lỗi xử lý ảnh {image_path}: {e}")
                continue
        
        if len(product_embeddings) > 0:
            # Chuyển list thành numpy array để tính toán nhanh
            self.product_vectors = np.array(product_embeddings)
            self.product_metadata = product_metadata_list
            print(f"Đã tạo cơ sở dữ liệu vector cho {len(self.product_vectors)} sản phẩm.")
        else:
            print("Không tạo được vector nào. Vui lòng kiểm tra lại đường dẫn ảnh trong CSV.")

    def find_similar_products(self, query_image_path: str, top_k: int = 5):
        """
        Tìm kiếm sản phẩm tương tự dựa trên ảnh truy vấn (Online Step).

        """
        # Kiểm tra cơ sở dữ liệu vector
        if self.product_vectors is None or len(self.product_vectors) == 0:
            print("Chưa có dữ liệu vector. Hãy chạy create_product_embeddings trước.")
            return []

        # Kiểm tra file ảnh truy vấn
        if not os.path.exists(query_image_path):
            print(f"Không tìm thấy ảnh truy vấn: {query_image_path}")
            return []

        # 1. Mã hóa ảnh truy vấn (người dùng upload)
        try:
            query_image = Image.open(query_image_path).convert("RGB")
            query_input = self.preprocess(query_image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                query_features = self.model.encode_image(query_input)
                
                # === BƯỚC KIỂM TRA AN TOÀN CHO QUERY ===
                if not torch.isfinite(query_features).all():
                    print("Lỗi: Ảnh truy vấn tạo ra vector hỏng (NaN/Inf).")
                    return []
                
                norm = query_features.norm(dim=-1, keepdim=True)
                if norm.item() == 0:
                    print("Lỗi: Ảnh truy vấn tạo ra vector rỗng (Norm=0).")
                    return []

                # Chuẩn hóa L2 vector truy vấn
                query_vector = query_features / norm
                query_vector = query_vector.cpu().numpy().flatten().reshape(1, -1)
                
        except Exception as e:
            print(f"Lỗi xử lý ảnh truy vấn: {e}")
            return []

        # 2. Tính độ tương đồng (Cosine Similarity)
        # Vì đã chuẩn hóa L2 và lọc sạch lỗi, hàm này sẽ chạy an toàn
        similarities = cosine_similarity(query_vector, self.product_vectors).flatten()

        # 3. Lấy Top K kết quả cao nhất
        # Sắp xếp giảm dần
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for i in top_indices:
            results.append({
                'info': self.product_metadata[i],
                'score': similarities[i]
            })
        
        return results