import os
import django
import random
from django.utils.text import slugify

# --- 1. SETUP DJANGO ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from store.models import Product, Category, Order, OrderItem, Review

# --- 2. CẤU HÌNH DỮ LIỆU ĐỂ SINH NGẪU NHIÊN ---
# Cấu trúc: Tên Danh Mục -> { 'brands': [...], 'models': [...], 'specs': [...] }
DATA_SOURCE = {
    "CPU": {
        "brands": ["Intel", "AMD"],
        "models": [
            "Core i3 12100F", "Core i3 13100", "Core i5 12400F", "Core i5 13600K", 
            "Core i7 12700K", "Core i7 14700K", "Core i9 13900K", "Core i9 14900KS",
            "Ryzen 3 4100", "Ryzen 5 5600X", "Ryzen 5 7600", "Ryzen 7 5800X3D", 
            "Ryzen 7 7800X3D", "Ryzen 9 5950X", "Ryzen 9 7950X"
        ],
        "specs": ["Box Chính Hãng", "Tray (Không Fan)", "Full Box", "Gaming", "Overclock"]
    },
    "GPU": {
        "brands": ["ASUS", "MSI", "Gigabyte", "Zotac", "Colorful", "Galax"],
        "models": [
            "RTX 3050", "RTX 3060", "RTX 4060", "RTX 4060 Ti", "RTX 4070 Super", 
            "RTX 4080", "RTX 4090", "GTX 1660 Super", "RX 6600", "RX 7600", "RX 7900 XTX"
        ],
        "specs": ["Gaming OC", "Ventus 2X", "Eagle", "ROG Strix", "TUF Gaming", "Aero ITX", "White Edition"]
    },
    "RAM": {
        "brands": ["Kingston", "Corsair", "G.Skill", "Adata", "TeamGroup", "Lexar"],
        "models": ["Fury Beast", "Vengeance LPX", "Vengeance RGB", "Trident Z5", "XPG Spectrix", "T-Force Delta"],
        "specs": ["8GB 3200MHz", "16GB 3200MHz", "16GB 3600MHz", "32GB 5600MHz DDR5", "32GB 6000MHz DDR5", "64GB Kit (2x32)"]
    },
    "Mainboard": {
        "brands": ["ASUS", "MSI", "Gigabyte", "ASRock"],
        "models": [
            "Prime H610M-K", "B660M Mortar", "B760M Gaming X", "Z790 Aorus Elite", 
            "B550M Steel Legend", "X570 TUF Gaming", "Z690 Tomahawk"
        ],
        "specs": ["DDR4", "DDR5 WiFi", "WiFi 6E", "DDR4 (Không Wifi)", "White Edition"]
    },
    "SSD": {
        "brands": ["Samsung", "Kingston", "Western Digital", "Crucial", "Lexar"],
        "models": ["980 Pro", "990 Pro", "NV2", "Black SN850X", "Blue SN570", "P3 Plus", "NM620"],
        "specs": ["250GB NVMe", "500GB NVMe Gen4", "1TB NVMe Gen4", "2TB NVMe Gen4", "500GB SATA 2.5", "1TB SATA"]
    },
    "HDD": {
        "brands": ["Seagate", "Western Digital", "Toshiba"],
        "models": ["Barracuda", "Blue", "Black", "Red Plus", "P300", "IronWolf"],
        "specs": ["1TB 7200rpm", "2TB 5400rpm", "4TB Camera", "6TB NAS", "2TB 7200rpm"]
    },
    "Case": {
        "brands": ["Xigmatek", "DeepCool", "NZXT", "Montech", "Mik", "Corsair"],
        "models": ["Gaming X 3F", "Aqua M", "H5 Flow", "H9 Elite", "Air 1000 Premium", "4000D Airflow"],
        "specs": ["Black", "White", "Pink", "Kèm 3 Fan RGB", "Kèm 4 Fan LED", "2 Mặt Kính"]
    },
    "Nguồn": {
        "brands": ["Corsair", "DeepCool", "MSI", "Cooler Master", "Asus", "Xigmatek"],
        "models": ["CV650", "PK650D", "MAG A750BN", "Elite V3", "TUF 750W", "X-Power III"],
        "specs": ["550W 80 Plus", "650W Bronze", "750W Gold", "850W Gold Modular", "1000W Platinum"]
    },
    "Màn hình": {
        "brands": ["LG", "Samsung", "Dell", "ASUS", "AOC", "ViewSonic"],
        "models": ["UltraGear 24GN650", "Odyssey G5", "UltraSharp U2422H", "TUF VG279Q1A", "24G2", "ProArt PA278QV"],
        "specs": ["24 inch 144Hz", "27 inch 2K 165Hz", "24 inch IPS 75Hz", "32 inch 4K Cong", "27 inch IPS 100Hz"]
    },
    "Chuột": {
        "brands": ["Logitech", "Razer", "SteelSeries", "Corsair", "DareU"],
        "models": ["G102 Lightsync", "G Pro X Superlight", "DeathAdder V3", "Rival 3", "Harpoon RGB", "EM908"],
        "specs": ["Black", "White", "Wireless", "Có Dây", "RGB"]
    },
    "Bàn phím": {
        "brands": ["Logitech", "DareU", "Akko", "Keychron", "Corsair", "E-Dra"],
        "models": ["G512 Carbon", "EK87", "3098B", "K2 Pro", "K68", "EK387"],
        "specs": ["Blue Switch", "Red Switch", "Brown Switch", "Silent Switch", "RGB Wireless"]
    }
}

def reset_and_seed_database():
    print("--- BẮT ĐẦU QUÁ TRÌNH TẠO 20 SẢN PHẨM MỖI LOẠI ---")
    
    # 1. XÓA DỮ LIỆU CŨ
    print("1. Đang xóa dữ liệu cũ...")
    try:
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Review.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        print("   -> Đã xóa sạch!")
    except Exception as e:
        print(f"   -> Lỗi khi xóa: {e}")

    # 2. TẠO DỮ LIỆU MỚI
    print("2. Đang tạo dữ liệu mới...")
    
    total_products = 0
    
    for cat_name, data in DATA_SOURCE.items():
        # Tạo danh mục
        cat_slug = slugify(cat_name)
        category, _ = Category.objects.get_or_create(name=cat_name, defaults={'slug': cat_slug})
        print(f"   + Đang tạo danh mục: {cat_name}...")

        # Tạo 20 sản phẩm cho mỗi danh mục
        # Dùng set để tránh trùng tên nếu random ra giống nhau
        created_names = set()
        attempts = 0
        
        while len(created_names) < 20 and attempts < 100:
            attempts += 1
            
            # Random các thành phần
            brand = random.choice(data["brands"])
            model = random.choice(data["models"])
            spec = random.choice(data["specs"])
            
            # Tạo tên đầy đủ: [Danh Mục] [Hãng] [Model] [Spec]
            # Ví dụ: GPU MSI RTX 3060 Gaming OC
            
            # Logic riêng cho CPU/GPU để tên tự nhiên hơn
            if cat_name in ["CPU", "GPU"]:
                 # CPU Intel Core i5... (Không cần lặp lại chữ CPU ở đầu nếu muốn tự nhiên, 
                 # nhưng bạn muốn search dễ nên ta sẽ để Tiền tố ở đầu)
                 base_name = f"{brand} {model} {spec}"
            else:
                 base_name = f"{brand} {model} {spec}"

            # Thêm mã số random để đảm bảo không trùng slug và nhìn chuyên nghiệp
            code = random.randint(10000, 99999)
            
            # Tên hiển thị cuối cùng: "RAM Kingston Fury 8GB - Mã 12345"
            full_name = f"{cat_name} {base_name} - Mã {code}"
            
            if full_name in created_names:
                continue
                
            created_names.add(full_name)
            
            # Random giá
            price = random.randint(10, 300) * 100000 # Từ 1 triệu đến 30 triệu
            # Chỉnh giá thấp cho chuột/phím
            if cat_name in ["Chuột", "Bàn phím", "Case"]:
                price = random.randint(2, 50) * 50000 # 100k - 2.5tr

            p_slug = slugify(f"{base_name}-{code}")

            Product.objects.create(
                category=category,
                name=full_name,
                slug=p_slug,
                description=f"Sản phẩm {full_name} chính hãng. Bảo hành 36 tháng. Hiệu năng vượt trội trong tầm giá.",
                price=price,
                available=True,
                image=None
            )
            total_products += 1

    print(f"\n--- HOÀN TẤT: Đã tạo tổng cộng {total_products} sản phẩm! ---")

if __name__ == '__main__':
    reset_and_seed_database()