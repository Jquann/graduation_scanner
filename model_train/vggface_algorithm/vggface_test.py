# VGGFace Face Recognition Test
import os
import numpy as np
from PIL import Image
import warnings
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import matplotlib.pyplot as plt
import cv2
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.preprocessing import image
import mtcnn

# Path to the main archive directory
ARCHIVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'archive')
LFW_DIR = os.path.join(ARCHIVE_DIR, 'lfw-funneled', 'lfw_funneled')
PAIRS_PATH = os.path.join(ARCHIVE_DIR, 'pairs.txt')

# Load pairs protocol
def load_lfw_pairs(pairs_path):
    pairs = []
    with open(pairs_path, 'r') as f:
        lines = f.readlines()[1:]  # skip header
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 3:
                # same person
                name, idx1, idx2 = parts
                img1 = os.path.join(LFW_DIR, name, f"{name}_{int(idx1):04d}.jpg")
                img2 = os.path.join(LFW_DIR, name, f"{name}_{int(idx2):04d}.jpg")
                pairs.append((img1, img2, True))
            elif len(parts) == 4:
                # different person
                name1, idx1, name2, idx2 = parts
                img1 = os.path.join(LFW_DIR, name1, f"{name1}_{int(idx1):04d}.jpg")
                img2 = os.path.join(LFW_DIR, name2, f"{name2}_{int(idx2):04d}.jpg")
                pairs.append((img1, img2, False))
    return pairs

# Initialize MTCNN for face detection
print("Initializing MTCNN face detector...")
detector = mtcnn.MTCNN()
print("MTCNN initialized successfully!")

# Initialize VGGFace model
print("Loading VGG16 model...")
vgg_model = VGG16(weights='imagenet', include_top=False, pooling='avg')
print("VGG16 model loaded successfully!")

def get_vgg_embedding(img_path):
    try:
        if not os.path.exists(img_path):
            return None
            
        # Load and preprocess image
        img = cv2.imread(img_path)
        if img is None:
            return None
        
        # Detect face using MTCNN
        result = detector.detect_faces(img)
        if not result:
            return None
        
        # Extract the face with highest confidence
        face = max(result, key=lambda x: x['confidence'])
        x, y, w, h = face['box']
        face_img = img[y:y+h, x:x+w]
        
        # Resize to 224x224 (VGG input size)
        face_img = cv2.resize(face_img, (224, 224))
        face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
        
        # Preprocess for VGG
        face_img = np.expand_dims(face_img, axis=0)
        face_img = preprocess_input(face_img)
        
        # Extract features using VGG16
        features = vgg_model.predict(face_img, verbose=0)
        return features.flatten()
        
    except Exception as e:
        warnings.warn(f"VGG embedding error for {img_path}: {str(e)}")
        return None

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Load pairs and run test
pairs = load_lfw_pairs(PAIRS_PATH)[:1000]  # Test with 100 pairs
print(f"Testing VGGFace with {len(pairs)} pairs...")

y_true = []
y_pred = []
skipped = 0

for i, (img1, img2, is_same) in enumerate(pairs):
    if i % 10 == 0:
        print(f"Processing pair {i+1}/{len(pairs)}")
    
    emb1 = get_vgg_embedding(img1)
    emb2 = get_vgg_embedding(img2)
    
    if emb1 is not None and emb2 is not None:
        sim = cosine_similarity(emb1, emb2)
        pred = sim > 0.5  # Threshold for same person
        y_true.append(is_same)
        y_pred.append(pred)
    else:
        skipped += 1

# Calculate metrics
if y_true:
    accuracy = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    
    print(f"\n=== VGGFace Results ===")
    print(f"Accuracy: {accuracy:.2%}")
    print(f"F1 Score: {f1:.2%}")
    print(f"Precision: {precision:.2%}")
    print(f"Recall: {recall:.2%}")
    print(f"Skipped pairs: {skipped}")
    
    # Create results visualization
    result_dir = os.path.join(os.path.dirname(__file__), 'result')
    os.makedirs(result_dir, exist_ok=True)
    
    metrics = ['Accuracy', 'F1 Score', 'Precision', 'Recall']
    values = [accuracy, f1, precision, recall]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(metrics, values, color='lightcoral', alpha=0.7)
    plt.title(f'VGGFace Performance on LFW Dataset ({len(pairs)} pairs)')
    plt.ylabel('Score')
    plt.ylim(0, 1)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f"{value:.3f}", ha='center', va='bottom')
    
    plt.tight_layout()
    
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'vggface_results_{timestamp}.png'
    plt.savefig(os.path.join(result_dir, filename))
    plt.show()
    
    print(f"Results saved to: {os.path.join(result_dir, filename)}")
else:
    print("No valid pairs processed!")
