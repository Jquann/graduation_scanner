# DeepFace-based Face Recognition Test
import os
import sys
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
import requests
from deepface import DeepFace
import pandas as pd

def load_image(image_path):
    """Load and preprocess image"""
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

def compare_faces(img1_path, img2_path, model_name='ArcFace', distance_metric='cosine', threshold=0.4):
    """Compare two face images using DeepFace"""
    try:
        # Use DeepFace with dlib backend and dlib model
        result = DeepFace.verify(
            img1_path=img1_path,
            img2_path=img2_path,
            model_name='ArcFace',
            detector_backend='opencv',
            distance_metric=distance_metric
        )
        is_same = result['verified']
        distance = result['distance']
        similarity = 1 - distance if distance_metric == 'cosine' else 1 / (1 + distance)
        return is_same, similarity
    except Exception as e:
        print(f"Error comparing faces: {e}")
        return False, 0.0

def main():
    print("Starting DeepFace-based Face Recognition Test...")
    
    # Path to LFW dataset
    base_path = os.path.join(os.path.dirname(__file__), '..', 'archive', 'lfw-funneled', 'lfw_funneled')
    pairs_file = os.path.join(os.path.dirname(__file__), '..', 'archive', 'pairs.txt')
    
    if not os.path.exists(pairs_file):
        print(f"Pairs file not found: {pairs_file}")
        return
    
    # Read pairs
    pairs = []
    with open(pairs_file, 'r') as f:
        lines = f.readlines()[1:]  # Skip header
        for line in lines[:1000]:  # Test with first 100 pairs (DeepFace is slower)
            parts = line.strip().split('\t')
            if len(parts) == 3:  # Same person
                name = parts[0]
                img1_num = int(parts[1])
                img2_num = int(parts[2])
                pairs.append((name, img1_num, name, img2_num, True))
            elif len(parts) == 4:  # Different persons
                name1 = parts[0]
                img1_num = int(parts[1])
                name2 = parts[2]
                img2_num = int(parts[3])
                pairs.append((name1, img1_num, name2, img2_num, False))
    
    print(f"Testing {len(pairs)} pairs...")
    
    y_true = []
    y_pred = []
    similarities = []
    skipped = 0
    
    # Use ArcFace model for DeepFace
    best_model = 'ArcFace'
    
    for i, (name1, img1_num, name2, img2_num, is_same) in enumerate(pairs):
        if i % 10 == 0:
            print(f"Processing pair {i+1}/{len(pairs)}")
        
        # Build image paths
        img1_path = os.path.join(base_path, name1, f"{name1}_{img1_num:04d}.jpg")
        img2_path = os.path.join(base_path, name2, f"{name2}_{img2_num:04d}.jpg")
        
        # Check if files exist
        if not os.path.exists(img1_path) or not os.path.exists(img2_path):
            skipped += 1
            continue
        
        # Compare faces using DeepFace
        prediction, similarity = compare_faces(img1_path, img2_path, model_name=best_model)
        
        if similarity == 0.0:  # Error occurred
            skipped += 1
            continue
        
        y_true.append(is_same)
        y_pred.append(prediction)
        similarities.append(similarity)
    
    if len(y_true) == 0:
        print("No valid pairs found!")
        return
    
    # Calculate metrics
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    accuracy = np.mean(y_true == y_pred)
    
    # Calculate confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    # Handle single class case
    if cm.size == 1:
        if y_true[0] == True:  # All true cases
            tp = np.sum(y_pred == True)
            fp = np.sum(y_pred == False)
            fn = 0
            tn = 0
        else:  # All false cases
            tn = np.sum(y_pred == False)
            fp = np.sum(y_pred == True)
            tp = 0
            fn = 0
    else:
        tn, fp, fn, tp = cm.ravel()
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"\n=== DeepFace Face Recognition Results ===")
    print(f"Model used: {best_model}")
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
    
    plt.figure(figsize=(12, 6))
    
    # Create subplot for metrics
    plt.subplot(1, 2, 1)
    bars = plt.bar(metrics, values, color='green', alpha=0.7)
    plt.title(f'DeepFace ({best_model}) Performance on LFW Dataset')
    plt.ylabel('Score')
    plt.ylim(0, 1)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f"{value:.3f}", ha='center', va='bottom')
    
    # Create subplot for similarity distribution
    plt.subplot(1, 2, 2)
    same_similarities = [sim for i, sim in enumerate(similarities) if y_true[i]]
    diff_similarities = [sim for i, sim in enumerate(similarities) if not y_true[i]]
    
    if same_similarities:
        plt.hist(same_similarities, bins=20, alpha=0.7, label='Same Person', color='green')
    if diff_similarities:
        plt.hist(diff_similarities, bins=20, alpha=0.7, label='Different Person', color='red')
    plt.xlabel('Similarity Score')
    plt.ylabel('Frequency')
    plt.title('Similarity Score Distribution')
    plt.legend()
    
    plt.tight_layout()
    
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'deepface_results_{timestamp}.png'
    plt.savefig(os.path.join(result_dir, filename))
    plt.savefig(os.path.join(result_dir, 'deepface_results.png'))
    plt.show()
    
    # Save detailed results
    try:
        results_df = pd.DataFrame({
            'y_true': y_true,
            'y_pred': y_pred,
            'similarities': similarities
        })
        results_df.to_csv(os.path.join(result_dir, f'deepface_detailed_results_{timestamp}.csv'), index=False)
    except:
        print("Could not save detailed results to CSV")
    
    print(f"\nResults saved to: {result_dir}")

if __name__ == "__main__":
    main()
