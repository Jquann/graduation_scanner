

# This script loads LFW pairs from archive/pairs.txt, extracts features with InsightFace, and computes accuracy.
import os
import numpy as np
from insightface.app import FaceAnalysis
from PIL import Image
from deepface import DeepFace
import warnings
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import matplotlib.pyplot as plt

ARCHIVE_DIR = os.path.join(os.path.dirname(__file__), 'archive')
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
app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0, det_size=(640, 640))


def get_embedding(img_path):
    if not os.path.exists(img_path):
        return None
    img = Image.open(img_path).convert('RGB')
    img = np.asarray(img)
    faces = app.get(img)
    if faces:
        return faces[0].embedding
    return None

# DeepFace embedding
def get_arcface_embedding(img_path):
    try:
        obj = DeepFace.represent(img_path=img_path, model_name='ArcFace', enforce_detection=False)
        return obj[0]['embedding'] if isinstance(obj, list) else obj['embedding']
    except Exception:
        return None


# DeepFace VGG-Face embedding
def get_vgg_embedding(img_path):
    try:
        obj = DeepFace.represent(img_path=img_path, model_name='VGG-Face', enforce_detection=False)
        return obj[0]['embedding'] if isinstance(obj, list) else obj['embedding']
    except Exception as e:
        warnings.warn(str(e))
        return None

pairs = load_lfw_pairs(PAIRS_PATH)[:100]

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

results = {
    'InsightFace': {'y_true': [], 'y_pred': [], 'skipped': 0},
    'ArcFace': {'y_true': [], 'y_pred': [], 'skipped': 0},
    'VGGFace': {'y_true': [], 'y_pred': [], 'skipped': 0}
}

for img1, img2, is_same in pairs:
    # InsightFace
    emb1 = get_embedding(img1)
    emb2 = get_embedding(img2)
    if emb1 is not None and emb2 is not None:
        sim = cosine_similarity(emb1, emb2)
        pred = sim > 0.5
        results['InsightFace']['y_true'].append(is_same)
        results['InsightFace']['y_pred'].append(pred)
    else:
        results['InsightFace']['skipped'] += 1

    # DeepFace ArcFace
    emb1 = get_arcface_embedding(img1)
    emb2 = get_arcface_embedding(img2)
    if emb1 is not None and emb2 is not None:
        sim = cosine_similarity(emb1, emb2)
        pred = sim > 0.5
        results['ArcFace']['y_true'].append(is_same)
        results['ArcFace']['y_pred'].append(pred)
    else:
        results['ArcFace']['skipped'] += 1

    # DeepFace VGG-Face
    emb1 = get_vgg_embedding(img1)
    emb2 = get_vgg_embedding(img2)
    if emb1 is not None and emb2 is not None:
        sim = cosine_similarity(emb1, emb2)
        pred = sim > 0.5
        results['VGGFace']['y_true'].append(is_same)
        results['VGGFace']['y_pred'].append(pred)
    else:
        results['VGGFace']['skipped'] += 1

# Calculate metrics and plot
metrics = ['accuracy', 'f1', 'precision', 'recall']
scores = {algo: {} for algo in results}
for algo in results:
    y_true = results[algo]['y_true']
    y_pred = results[algo]['y_pred']
    scores[algo]['accuracy'] = accuracy_score(y_true, y_pred) if y_true else 0
    scores[algo]['f1'] = f1_score(y_true, y_pred) if y_true else 0
    scores[algo]['precision'] = precision_score(y_true, y_pred) if y_true else 0
    scores[algo]['recall'] = recall_score(y_true, y_pred) if y_true else 0
    print(f"{algo}: accuracy={scores[algo]['accuracy']:.2%}, f1={scores[algo]['f1']:.2%}, precision={scores[algo]['precision']:.2%}, recall={scores[algo]['recall']:.2%}, skipped={results[algo]['skipped']}")

# Plot


# Ensure result folder exists inside model_train
result_dir = os.path.join(os.path.dirname(__file__), 'result')
os.makedirs(result_dir, exist_ok=True)

fig, ax = plt.subplots()
bar_width = 0.2
index = np.arange(len(metrics))
for i, algo in enumerate(results):
    values = [scores[algo][m] for m in metrics]
    bars = ax.bar(index + i * bar_width, values, bar_width, label=algo)
    # Add metric values on top of bars
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f"{value:.2f}", ha='center', va='bottom', fontsize=8)
ax.set_xlabel('Metric')
ax.set_ylabel('Score')
ax.set_title(f'Face Recognition Comparison (LFW, {len(pairs)} pairs)')
ax.set_xticks(index + bar_width)
ax.set_xticklabels(metrics)
ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.tight_layout()
plt.savefig(os.path.join(result_dir, 'face_recognition_comparison.png'))
plt.show()
