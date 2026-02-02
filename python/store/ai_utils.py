import torch
from torchvision import transforms
from PIL import Image
import os
from django.conf import settings
import torch.nn as nn
from torchvision import models

# Danh sách 11 nhãn theo thứ tự train (Cực kỳ quan trọng phải đúng thứ tự)
LABELS = ['cables', 'case', 'cpu', 'gpu', 'hdd', 'headset', 'keyboard', 'monitor', 'motherboard', 'mouse', 'ram']

MODEL_PATH = os.path.join(settings.BASE_DIR, r'C:\Users\tungd\Downloads\resnet50_pc_parts_finetuned.pth')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Khởi tạo model
model = models.resnet50(pretrained=False)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, len(LABELS)) 

# Load weights
try:
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        model.to(device)
        model.eval()
        print("AI Model loaded!")
    else:
        print("AI Model file missing!")
        model = None
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

def predict_image_class(image_file):
    if model is None: return None
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    try:
        image = Image.open(image_file).convert('RGB')
        img_tensor = transform(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            outputs = model(img_tensor)
            _, predicted = torch.max(outputs, 1)
            
        return LABELS[predicted.item()]
    except Exception as e:
        print(f"Prediction error: {e}")
        return None