#!/usr/bin/env python3
"""
Face recognition core functionality using InsightFace library.
This module provides tools for detecting faces, extracting their embeddings,
calculating similarities, and managing dynamic thresholds for recognition.
"""

import numpy as np
import insightface
from typing import List, Tuple, Optional, Any
import cv2
from insightface.utils.face_align import norm_crop # Import for face alignment

from config import Config
from DeepFaceModel.FasNet import Fasnet


class FaceRecognitionEngine:
    """
    Handles all face recognition operations, including model initialization,
    face detection, encoding extraction, and similarity calculations.
    """
    
    def __init__(self, performance_mode: str = 'balanced'):
        """
        Initializes the FaceRecognitionEngine with a specified performance mode.

        Args:
            performance_mode (str): The desired performance mode ('balanced', 'high', etc.).
                                    This influences the configuration settings for face detection.
        """
        self.config = Config.get_performance_config(performance_mode)
        self.face_app = None
        self.fasnet_model = None # Initialize Fasnet model
        self.last_spoof_error = "" # Initialize last spoofing error message
        self.initialize_model()
    
    def initialize_model(self):
        """
        Initializes the InsightFace model for face analysis.
        It sets up the provider and detection size based on the configuration.
        Raises a RuntimeError if the model fails to load.
        """
        print("Loading InsightFace model...")
        try:
            # Initialize FaceAnalysis application with the specified provider
            self.face_app = insightface.app.FaceAnalysis(
                providers=[Config.INSIGHTFACE_PROVIDER]
            )
            # Prepare the model for inference, setting the context ID and detection size
            self.face_app.prepare(ctx_id=0, det_size=self.config['det_size'])
            print("InsightFace model loaded successfully")

            # Initialize Fasnet model
            self.fasnet_model = Fasnet()
            print("Fasnet anti-spoofing model loaded successfully")
        except Exception as e:
            print(f"Error loading face recognition or anti-spoofing models: {e}")
            raise # Re-raise the exception to indicate a critical failure

    def process_single_face_with_spoofing(self, face: Any, frame: np.ndarray) -> Optional[Tuple[np.ndarray, bool, float]]:
        """
        Processes a single detected face, performs anti-spoofing, and extracts its embedding.

        Args:
            face (Any): Detected face object from InsightFace.
            frame (np.ndarray): The original input video frame.

        Returns:
            Optional[Tuple[np.ndarray, bool, float]]: A tuple containing the normalized face embedding,
                                                      a boolean indicating if it's a real face (not spoof),
                                                      and the spoofing confidence. Returns None if spoofing
                                                      is detected or an error occurs.
        """
        x1, y1, x2, y2 = face.bbox.astype(int)
        w, h = x2 - x1, y2 - y1

        try:
            # Align face using facial landmarks
            aligned_face = norm_crop(frame, landmark=face.kps)
            aligned_face = cv2.cvtColor(aligned_face, cv2.COLOR_BGR2RGB)
            aligned_face = cv2.resize(aligned_face, self.config['recognition_size'])

            # Perform spoofing check
            is_real, spoof_confidence = self.detect_spoofing(aligned_face)
            if not is_real:
                # Check if the detection was due to model not being initialized
                if spoof_confidence == 0.0 and "Fasnet model not initialized" in self.last_spoof_error: # Assuming I'll add a way to store the last error
                    print(f"⚠️ Anti-spoofing inactive: {self.last_spoof_error}")
                else:
                    print(f"⚠️ Spoofing attempt detected! (Confidence: {spoof_confidence*100:.1f}%)")
                return None # Return None if spoofing is detected
            else:
                print(f"✅ Face is real. (Spoofing Confidence: {spoof_confidence*100:.1f}%)")

            # Get face embedding
            # The embedding is already normalized by InsightFace when accessed via normed_embedding
            current_embedding = face.normed_embedding

            return current_embedding, is_real, spoof_confidence

        except Exception as e:
            print(f"❌ Failed to process face with spoofing check: {e}")
            return None
    
    def detect_faces(self, image: np.ndarray) -> List[Any]:
        """
        Detects faces in a given image using the initialized InsightFace model.

        Args:
            image (np.ndarray): The input image (numpy array) in RGB format.

        Returns:
            List[Any]: A list of detected face objects, each containing bounding box,
                       landmarks, and other face attributes. Returns an empty list on error.

        Raises:
            RuntimeError: If the face recognition model has not been initialized.
        """
        if self.face_app is None:
            raise RuntimeError("Face recognition model not initialized")
        
        try:
            faces = self.face_app.get(image)
            return faces
        except Exception as e:
            print(f"Face detection error: {e}")
            return []
    
    def extract_face_encoding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extracts the face encoding (embedding) from the first detected face in an image.

        Args:
            image (np.ndarray): The input image (numpy array) in RGB format.

        Returns:
            Optional[np.ndarray]: A numpy array representing the normalized face embedding
                                  if a face is detected, otherwise None.
        """
        faces = self.detect_faces(image)
        
        if not faces:
            return None
        
        if len(faces) > 1:
            print(f"Multiple faces detected ({len(faces)}), using the first one")
        
        # Return the normalized embedding of the first face
        return faces[0].normed_embedding
    
    def extract_multiple_encodings(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Extracts all face encodings (embeddings) from all detected faces in an image.

        Args:
            image (np.ndarray): The input image (numpy array) in RGB format.

        Returns:
            List[np.ndarray]: A list of numpy arrays, each representing a normalized face embedding.
        """
        faces = self.detect_faces(image)
        encodings = []
        
        for face in faces:
            processed_result = self.process_single_face_with_spoofing(face, image)
            if processed_result:
                embedding, is_real, _ = processed_result
                if is_real:
                    encodings.append(embedding)
        
        return encodings
    
    def calculate_similarity(self, encoding1: np.ndarray, encoding2: np.ndarray) -> float:
        """
        Calculates the cosine similarity between two face encodings.
        Cosine similarity measures the cosine of the angle between two vectors.

        Args:
            encoding1 (np.ndarray): The first face encoding (numpy array).
            encoding2 (np.ndarray): The second face encoding (numpy array).

        Returns:
            float: The cosine similarity score, ranging from -1.0 to 1.0.
                   Returns 0.0 if an error occurs or if norms are zero.
        """
        try:
            # Ensure inputs are numpy arrays for consistent calculations
            enc1 = np.array(encoding1)
            enc2 = np.array(encoding2)
            
            # Calculate cosine similarity using dot product and L2 norms
            dot_product = np.dot(enc1, enc2)
            norm1 = np.linalg.norm(enc1)
            norm2 = np.linalg.norm(enc2)
            
            if norm1 > 0 and norm2 > 0:
                similarity = dot_product / (norm1 * norm2)
                return float(similarity)
            
            return 0.0 # Return 0.0 if either norm is zero to avoid division by zero
        except Exception as e:
            print(f"Similarity calculation error: {e}")
            return 0.0
    
    def calculate_batch_similarity(self, encodings_list: List[np.ndarray],
                                  target_encoding: np.ndarray) -> Tuple[float, float]:
        """
        Calculates batch similarity between a list of face encodings and a target encoding.
        It enhances accuracy by trimming outliers and applying a weighted average.

        Args:
            encodings_list (List[np.ndarray]): A list of face encodings to compare.
            target_encoding (np.ndarray): The single target face encoding.

        Returns:
            Tuple[float, float]: A tuple containing:
                                 - weighted_similarity (float): The best similarity score after
                                   outlier removal and weighted averaging.
                                 - avg_similarity (float): The average similarity score of the
                                   trimmed list.
                                 Returns (0.0, 0.0) if the input list is empty or an error occurs.
        """
        if not encodings_list:
            return 0.0, 0.0
        
        similarities = []
        
        try:
            target_enc = np.array(target_encoding)
            
            # Calculate similarity for each encoding in the list against the target
            for encoding in encodings_list:
                similarity = self.calculate_similarity(encoding, target_enc)
                similarities.append(similarity)
            
            if not similarities:
                return 0.0, 0.0
            
            # Remove outliers for better accuracy: sort and trim extreme values
            sorted_similarities = sorted(similarities)
            
            if len(sorted_similarities) >= 5:
                # Remove bottom 20% and top 20% to mitigate extreme values
                trim_count = max(1, len(sorted_similarities) // 5)
                trimmed_similarities = sorted_similarities[trim_count:-trim_count]
            else:
                # If fewer than 5 similarities, no trimming is applied
                trimmed_similarities = sorted_similarities
            
            if trimmed_similarities:
                best_similarity = max(trimmed_similarities)
                avg_similarity = np.mean(trimmed_similarities)
                
                # Weighted average: give best similarity higher weight for robustness
                weighted_similarity = (best_similarity * 0.7) + (avg_similarity * 0.3)
                
                return weighted_similarity, avg_similarity
            else:
                # Fallback if trimming results in an empty list (e.g., very small input list)
                return max(similarities), np.mean(similarities)
                
        except Exception as e:
            print(f"Batch similarity calculation error: {e}")
            return 0.0, 0.0
    
    def calculate_dynamic_threshold(self, num_encodings: int, attempt_count: int,
                                   base_threshold: float = 0.35) -> float:
        """
        Calculates a dynamic similarity threshold based on the number of encodings
        and the current attemptcan  count. This adjusts the required similarity for a match.

        Args:
            num_encodings (int): The number of face encodings available for comparison.
            attempt_count (int): The current attempt number for recognition.
            base_threshold (float): The initial base similarity threshold.

        Returns:
            float: The dynamically adjusted similarity threshold, clamped within
                   configured minimum and maximum values.
        """
        # Apply a bonus for more available encodings (makes threshold lower, easier to match)
        encoding_bonus = min(num_encodings * Config.ENCODING_BONUS, 0.05)
        
        # Apply a penalty for more attempts (makes threshold higher, harder to match)
        attempt_penalty = min(attempt_count * Config.ATTEMPT_PENALTY, 0.03)
        
        # Calculate dynamic threshold by adjusting the base threshold
        dynamic_threshold = base_threshold - encoding_bonus + attempt_penalty
        
        # Clamp the dynamic threshold between configured min and max values
        min_threshold = self.config.get('similarity_threshold_min', 0.28)
        max_threshold = self.config.get('similarity_threshold_max', 0.45)
        
        return max(min_threshold, min(max_threshold, dynamic_threshold))
    
    def verify_face_in_image(self, image_path: str) -> bool:
        """
        Verifies if at least one face exists in an image file specified by its path.

        Args:
            image_path (str): The file path to the image.

        Returns:
            bool: True if one or more faces are detected, False otherwise or on error.
        """
        try:
            # Read the image from the specified path
            image = cv2.imread(image_path)
            if image is None:
                print(f"Error: Could not read image from {image_path}")
                return False
            
            # Convert the image from BGR (OpenCV default) to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            faces = self.detect_faces(image_rgb)
            
            return len(faces) > 0
        except Exception as e:
            print(f"Face verification error: {e}")
            return False
    
    def get_face_bounding_boxes(self, image: np.ndarray) -> List[List[int]]:
        """
        Retrieves the bounding boxes for all faces detected in an image.

        Args:
            image (np.ndarray): The input image (numpy array) in RGB format.

        Returns:
            List[List[int]]: A list of bounding boxes, where each bounding box is
                             represented as [x1, y1, x2, y2] (integers).
        """
        faces = self.detect_faces(image)
        bounding_boxes = []
        
        for face in faces:
            # Extract and convert bounding box coordinates to integers
            bbox = face.bbox.astype(int)
            bounding_boxes.append([bbox[0], bbox[1], bbox[2], bbox[3]])
        
        return bounding_boxes
    
    def detect_spoofing(self, face_img: np.ndarray, bbox: Optional[Tuple[int, int, int, int]] = None) -> Tuple[bool, float]:
        """
        Detect if the face is real or a spoof attempt using Fasnet model.

        Args:
            face_img (np.ndarray): Cropped face image (numpy array) or full frame.
            bbox (Optional[Tuple[int, int, int, int]]): Optional bounding box (x, y, w, h)
                                                        if face_img is a full frame.

        Returns:
            Tuple[bool, float]: (is_real, confidence) where is_real is a boolean and confidence is a float 0-1.
        """
        if self.fasnet_model is None:
            error_msg = "Fasnet model not initialized for spoof detection."
            self.last_spoof_error = error_msg
            print(f"⚠️ {error_msg}")
            return False, 0.0

        try:
            if bbox is not None:
                x, y, w, h = bbox
                is_real, confidence = self.fasnet_model.analyze(face_img, (x, y, w, h))
            else:
                # If no bbox, assume face_img is already cropped and use its dimensions as the bbox
                is_real, confidence = self.fasnet_model.analyze(face_img, (0, 0, face_img.shape[1], face_img.shape[0]))
            
            self.last_spoof_error = "" # Clear error on successful detection
            return is_real, confidence
        except Exception as e:
            error_msg = f"Spoof detection error: {str(e)}"
            self.last_spoof_error = error_msg
            print(f"⚠️ {error_msg}")
            return False, 0.0

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocesses an image to ensure it is in RGB format, which is typically
        required for face detection models. Handles grayscale, RGBA, and BGR inputs.

        Args:
            image (np.ndarray): The input image (numpy array).

        Returns:
            np.ndarray: The preprocessed image in RGB format.
        """
        # Convert to RGB if the image is grayscale (2 dimensions)
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        # Convert to RGB if the image is RGBA (4 channels)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        # Assume BGR and convert to RGB if the image has 3 channels
        elif image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        return image
    
    def compare_faces(self, face_encoding1: np.ndarray, face_encoding2: np.ndarray,
                     threshold: float = 0.35) -> Tuple[bool, float]:
        """
        Compares two face encodings to determine if they belong to the same person
        based on a given similarity threshold.

        Args:
            face_encoding1 (np.ndarray): The first face encoding.
            face_encoding2 (np.ndarray): The second face encoding.
            threshold (float): The similarity threshold above which faces are considered a match.

        Returns:
            Tuple[bool, float]: A tuple containing:
                                - is_match (bool): True if similarity is above the threshold, False otherwise.
                                - similarity_score (float): The calculated cosine similarity score.
        """
        similarity = self.calculate_similarity(face_encoding1, face_encoding2)
        is_match = similarity > threshold
        return is_match, similarity
