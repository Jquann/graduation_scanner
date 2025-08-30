# InsightFace Face Recognition Test
import os
import numpy as np
from insightface.app import FaceAnalysis
from PIL import Image
import warnings
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import matplotlib.pyplot as plt
import cv2

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

# Initialize InsightFace
print("Initializing InsightFace...")
app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0, det_size=(640, 640))
print("InsightFace initialized successfully!")

def get_embedding(img_path):
    if not os.path.exists(img_path):
        return None
    try:
        img = Image.open(img_path).convert('RGB')
        img = np.asarray(img)
        faces = app.get(img)
        if faces:
            return faces[0].embedding
        return None
    except Exception as e:
        warnings.warn(f"InsightFace embedding error for {img_path}: {str(e)}")
        return None

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Load pairs and run test
pairs = load_lfw_pairs(PAIRS_PATH)[:1000]  # Test with 100 pairs
print(f"Testing InsightFace with {len(pairs)} pairs...")

y_true = []
y_pred = []
skipped = 0

for i, (img1, img2, is_same) in enumerate(pairs):
    if i % 10 == 0:
        print(f"Processing pair {i+1}/{len(pairs)}")
    
    emb1 = get_embedding(img1)
    emb2 = get_embedding(img2)
    
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
    
    print(f"\n=== InsightFace Results ===")
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
    bars = plt.bar(metrics, values, color='skyblue', alpha=0.7)
    plt.title(f'InsightFace Performance on LFW Dataset ({len(pairs)} pairs)')
    plt.ylabel('Score')
    plt.ylim(0, 1)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f"{value:.3f}", ha='center', va='bottom')
    
    plt.tight_layout()
    
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'insightface_results_{timestamp}.png'
    plt.savefig(os.path.join(result_dir, filename))
    plt.show()
    
    print(f"Results saved to: {os.path.join(result_dir, filename)}")
else:
    print("No valid pairs processed!")
