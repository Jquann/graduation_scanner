#!/usr/bin/env python3
"""
Face recognition core functionality using InsightFace
"""

import numpy as np
import insightface
from typing import List, Tuple, Optional, Any
import cv2

from config import Config


class FaceRecognitionEngine:
    """Handles all face recognition operations"""
    
    def __init__(self, performance_mode='balanced'):
        self.config = Config.get_performance_config(performance_mode)
        self.face_app = None
        self.initialize_model()
    
    def initialize_model(self):
        """Initialize InsightFace model"""
        print("Loading InsightFace model...")
        try:
            self.face_app = insightface.app.FaceAnalysis(
                providers=[Config.INSIGHTFACE_PROVIDER]
            )
            self.face_app.prepare(ctx_id=0, det_size=self.config['det_size'])
            print("InsightFace model loaded successfully")
        except Exception as e:
            print(f"Error loading InsightFace model: {e}")
            raise
    
    def detect_faces(self, image: np.ndarray) -> List[Any]:
        """Detect faces in an image"""
        if self.face_app is None:
            raise RuntimeError("Face recognition model not initialized")
        
        try:
            faces = self.face_app.get(image)
            return faces
        except Exception as e:
            print(f"Face detection error: {e}")
            return []
    
    def extract_face_encoding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract face encoding from an image"""
        faces = self.detect_faces(image)
        
        if not faces:
            return None
        
        if len(faces) > 1:
            print(f"Multiple faces detected ({len(faces)}), using the first one")
        
        # Return the normalized embedding of the first face
        return faces[0].normed_embedding
    
    def extract_multiple_encodings(self, image: np.ndarray) -> List[np.ndarray]:
        """Extract all face encodings from an image"""
        faces = self.detect_faces(image)
        encodings = []
        
        for face in faces:
            if hasattr(face, 'normed_embedding'):
                encodings.append(face.normed_embedding)
        
        return encodings
    
    def calculate_similarity(self, encoding1: np.ndarray, encoding2: np.ndarray) -> float:
        """Calculate cosine similarity between two face encodings"""
        try:
            # Ensure inputs are numpy arrays
            enc1 = np.array(encoding1)
            enc2 = np.array(encoding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(enc1, enc2)
            norm1 = np.linalg.norm(enc1)
            norm2 = np.linalg.norm(enc2)
            
            if norm1 > 0 and norm2 > 0:
                similarity = dot_product / (norm1 * norm2)
                return float(similarity)
            
            return 0.0
        except Exception as e:
            print(f"Similarity calculation error: {e}")
            return 0.0
    
    def calculate_batch_similarity(self, encodings_list: List[np.ndarray], 
                                  target_encoding: np.ndarray) -> Tuple[float, float]:
        """
        Calculate batch similarity with enhanced accuracy
        Returns: (best_similarity, average_similarity)
        """
        if not encodings_list:
            return 0.0, 0.0
        
        similarities = []
        
        try:
            target_enc = np.array(target_encoding)
            
            for encoding in encodings_list:
                similarity = self.calculate_similarity(encoding, target_enc)
                similarities.append(similarity)
            
            if not similarities:
                return 0.0, 0.0
            
            # Remove outliers for better accuracy
            sorted_similarities = sorted(similarities)
            
            if len(sorted_similarities) >= 5:
                # Remove bottom 20% and top 20%
                trim_count = max(1, len(sorted_similarities) // 5)
                trimmed_similarities = sorted_similarities[trim_count:-trim_count]
            else:
                trimmed_similarities = sorted_similarities
            
            if trimmed_similarities:
                best_similarity = max(trimmed_similarities)
                avg_similarity = np.mean(trimmed_similarities)
                
                # Weighted average - give best similarity higher weight
                weighted_similarity = (best_similarity * 0.7) + (avg_similarity * 0.3)
                
                return weighted_similarity, avg_similarity
            else:
                return max(similarities), np.mean(similarities)
                
        except Exception as e:
            print(f"Batch similarity calculation error: {e}")
            return 0.0, 0.0
    
    def calculate_dynamic_threshold(self, num_encodings: int, attempt_count: int,
                                   base_threshold: float = 0.35) -> float:
        """Calculate dynamic similarity threshold based on context"""
        # Bonus for more encodings
        encoding_bonus = min(num_encodings * Config.ENCODING_BONUS, 0.05)
        
        # Penalty for more attempts
        attempt_penalty = min(attempt_count * Config.ATTEMPT_PENALTY, 0.03)
        
        # Calculate dynamic threshold
        dynamic_threshold = base_threshold - encoding_bonus + attempt_penalty
        
        # Clamp between min and max values
        min_threshold = self.config.get('similarity_threshold_min', 0.28)
        max_threshold = self.config.get('similarity_threshold_max', 0.45)
        
        return max(min_threshold, min(max_threshold, dynamic_threshold))
    
    def verify_face_in_image(self, image_path: str) -> bool:
        """Verify if a face exists in an image file"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return False
            
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            faces = self.detect_faces(image_rgb)
            
            return len(faces) > 0
        except Exception as e:
            print(f"Face verification error: {e}")
            return False
    
    def get_face_bounding_boxes(self, image: np.ndarray) -> List[List[int]]:
        """Get bounding boxes for all detected faces"""
        faces = self.detect_faces(image)
        bounding_boxes = []
        
        for face in faces:
            bbox = face.bbox.astype(int)
            bounding_boxes.append([bbox[0], bbox[1], bbox[2], bbox[3]])
        
        return bounding_boxes
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better face detection"""
        # Convert to RGB if needed
        if len(image.shape) == 2:  # Grayscale
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:  # RGBA
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        elif image.shape[2] == 3:
            # Assume BGR, convert to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        return image
    
    def compare_faces(self, face_encoding1: np.ndarray, face_encoding2: np.ndarray,
                     threshold: float = 0.35) -> Tuple[bool, float]:
        """
        Compare two face encodings
        Returns: (is_match, similarity_score)
        """
        similarity = self.calculate_similarity(face_encoding1, face_encoding2)
        is_match = similarity > threshold
        return is_match, similarity