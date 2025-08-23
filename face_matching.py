#!/usr/bin/env python3
"""
Face matching logic for recognition
"""

import time
import queue
import numpy as np
from typing import List, Optional
from datetime import datetime

from models import RecognitionResult
from database import StudentDatabase


class FaceMatcher:
    """Handles face matching logic"""
    
    def __init__(self, face_engine, qr_manager, config):
        self.face_engine = face_engine
        self.qr_manager = qr_manager
        self.config = config
        self.database = StudentDatabase()
        
        # Matching state
        self.face_encodings_buffer = []
        self.last_match_time = 0
        self.consecutive_matches = 0
    
    def process_encodings(self, face_queue: queue.Queue, result_queue: queue.Queue):
        """Process face encodings from queue and perform matching"""
        current_time = time.time()
        
        # Collect face encodings
        self._collect_encodings(face_queue, current_time)
        
        # Clean expired encodings
        self._clean_expired_encodings(current_time)
        
        # Perform matching if conditions are met
        if self._should_perform_matching(current_time):
            self._perform_matching(result_queue, current_time)
    
    def _collect_encodings(self, face_queue: queue.Queue, current_time: float):
        """Collect face encodings from queue"""
        try:
            while True:
                face_encoding = face_queue.get_nowait()
                self.face_encodings_buffer.append({
                    'encoding': face_encoding,
                    'timestamp': current_time
                })
                
                # Maintain buffer size
                if len(self.face_encodings_buffer) > self.config['face_buffer_size']:
                    self.face_encodings_buffer.pop(0)
        except queue.Empty:
            pass
    
    def _clean_expired_encodings(self, current_time: float):
        """Remove expired face encodings from buffer"""
        self.face_encodings_buffer = [
            item for item in self.face_encodings_buffer
            if current_time - item['timestamp'] < 3.0  # Keep for 3 seconds
        ]
    
    def _should_perform_matching(self, current_time: float) -> bool:
        """Check if matching should be performed"""
        qr_data = self.qr_manager.get_current_qr()
        
        if not qr_data:
            return False
        
        if not self.face_encodings_buffer:
            return False
        
        if self.qr_manager.is_max_attempts_reached():
            return False
        
        cooldown_passed = (current_time - self.last_match_time) > self.config['match_cooldown']
        
        return cooldown_passed
    
    def _perform_matching(self, result_queue: queue.Queue, current_time: float):
        """Perform face matching against database"""
        qr_data = self.qr_manager.get_current_qr()
        if not qr_data:
            return
        
        student = self.database.find_student_by_id(qr_data.data)
        
        if not student:
            # Student not found
            if self.qr_manager.get_attempt_count() == 0:
                self.qr_manager.increment_attempt()
                result_queue.put(("student_not_found", {
                    "student_id": qr_data.data,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }))
            self.last_match_time = current_time
            return
        
        # Increment attempt counter
        self.qr_manager.increment_attempt()
        
        # Get recent encodings for matching
        recent_encodings = [
            item['encoding'] for item in self.face_encodings_buffer[-5:]
        ]
        
        if not recent_encodings:
            return
        
        # Calculate similarity
        target_encoding = np.array(student["face_encoding"])
        best_similarity, avg_similarity = self.face_engine.calculate_batch_similarity(
            recent_encodings, target_encoding
        )
        
        # Calculate dynamic threshold
        dynamic_threshold = self.face_engine.calculate_dynamic_threshold(
            len(recent_encodings),
            self.qr_manager.get_attempt_count(),
            self.config.get('similarity_threshold_base', 0.35)
        )
        
        print(f"Attempt {self.qr_manager.get_attempt_count()}: {student['name']} - "
              f"Best={best_similarity:.3f}, Avg={avg_similarity:.3f}, "
              f"Threshold={dynamic_threshold:.3f}")
        
        # Record attempt
        self.qr_manager.add_match_attempt(
            best_similarity, avg_similarity, dynamic_threshold,
            best_similarity > dynamic_threshold
        )
        
        if best_similarity > dynamic_threshold:
            self.consecutive_matches += 1
            
            # Need consecutive matches for confirmation
            if self.consecutive_matches >= 2:  # Config.CONSECUTIVE_MATCHES_THRESHOLD
                # SUCCESSFUL MATCH
                result = RecognitionResult(
                    student_id=student["student_id"],
                    name=student["name"],
                    faculty=student["faculty"],
                    graduation_level=student["graduation_level"],
                    similarity=best_similarity,
                    avg_similarity=avg_similarity,
                    confidence_level=min(self.consecutive_matches, 5),
                    total_attempts=self.qr_manager.get_attempt_count()
                )
                
                result_queue.put(("match_found", result.to_display_dict()))
                
                # Reset for next QR
                self.face_encodings_buffer.clear()
                self.consecutive_matches = 0
                self.qr_manager.clear_current_qr()
        else:
            # Similarity not enough
            self.consecutive_matches = 0
            
            # Report low similarity
            if self.qr_manager.get_attempt_count() < self.config['min_match_attempts']:
                if best_similarity > 0.2:
                    result_queue.put(("similarity_low", {
                        "student_id": student["student_id"],
                        "student_name": student["name"],
                        "similarity": best_similarity,
                        "required": dynamic_threshold,
                        "attempt": self.qr_manager.get_attempt_count(),
                        "max_attempts": self.config['max_match_attempts'],
                        "suggestion": "Please position face closer to camera",
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }))
        
        self.last_match_time = current_time
    
    def force_match(self, student_id: str) -> Optional[RecognitionResult]:
        """Force a manual match for a student"""
        student = self.database.find_student_by_id(student_id)
        
        if not student:
            return None
        
        result = RecognitionResult(
            student_id=student["student_id"],
            name=student["name"],
            faculty=student["faculty"],
            graduation_level=student["graduation_level"],
            similarity=1.0,
            avg_similarity=1.0,
            confidence_level=5,
            total_attempts=0,
            manual_override=True
        )
        
        return result
    
    def reset_state(self):
        """Reset matching state"""
        self.face_encodings_buffer.clear()
        self.consecutive_matches = 0
        self.last_match_time = 0