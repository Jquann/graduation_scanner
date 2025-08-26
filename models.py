#!/usr/bin/env python3
"""
Data models and structures for Graduation Scanner
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import time


@dataclass
class Student:
    """Student data model"""
    student_id: str
    name: str
    faculty: str
    graduation_level: str
    photo_path: str
    qr_code_path: str
    face_encoding: List[float]
    registered_time: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "faculty": self.faculty,
            "graduation_level": self.graduation_level,
            "photo_path": self.photo_path,
            "qr_code_path": self.qr_code_path,
            "face_encoding": self.face_encoding,
            "registered_time": self.registered_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Student':
        """Create Student from dictionary"""
        return cls(**data)


@dataclass
class QRData:
    """QR code data model with persistence tracking"""
    data: str
    source: str
    load_time: float = field(default_factory=time.time)
    attempt_count: int = 0
    match_history: List[Dict] = field(default_factory=list)
    
    def is_expired(self, timeout: float) -> bool:
        """Check if QR data has expired"""
        return (time.time() - self.load_time) > timeout
    
    def get_remaining_time(self, timeout: float) -> float:
        """Get remaining time before expiry"""
        return max(0, timeout - (time.time() - self.load_time))
    
    def increment_attempt(self):
        """Increment attempt counter"""
        self.attempt_count += 1
    
    def add_match_attempt(self, similarity: float, avg_similarity: float, 
                         threshold: float, success: bool):
        """Record a match attempt"""
        self.match_history.append({
            'attempt': self.attempt_count,
            'best_similarity': similarity,
            'avg_similarity': avg_similarity,
            'threshold': threshold,
            'timestamp': time.time(),
            'success': success
        })


@dataclass
class RecognitionResult:
    """Recognition result model"""
    student_id: str
    name: str
    faculty: str
    graduation_level: str
    similarity: float
    avg_similarity: float
    confidence_level: int
    total_attempts: int
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    manual_override: bool = False
    
    def to_display_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display"""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "faculty": self.faculty,
            "graduation_level": self.graduation_level,
            "similarity": self.similarity,
            "avg_similarity": self.avg_similarity,
            "confidence_level": self.confidence_level,
            "total_attempts": self.total_attempts,
            "timestamp": self.timestamp,
            "manual_override": self.manual_override
        }


@dataclass
class FaceDetectionResult:
    """Face detection result model"""
    bbox: List[int]  # [x1, y1, x2, y2]
    confidence: float
    timestamp: float
    encoding: Optional[Any] = None  # numpy array
    is_spoof: bool = False # New field to indicate if the detected face is a spoof
    
    def scale_bbox(self, scale_x: float, scale_y: float) -> List[int]:
        """Scale bounding box coordinates"""
        return [
            int(self.bbox[0] * scale_x),
            int(self.bbox[1] * scale_y),
            int(self.bbox[2] * scale_x),
            int(self.bbox[3] * scale_y)
        ]


@dataclass
class PerformanceStats:
    """Performance statistics model"""
    fps_counter: int = 0
    last_fps_time: float = field(default_factory=time.time)
    current_fps: int = 0
    detection_count: int = 0
    recognition_count: int = 0
    
    def update_fps(self) -> int:
        """Update and return current FPS"""
        current_time = time.time()
        if current_time - self.last_fps_time > 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.last_fps_time = current_time
        else:
            self.fps_counter += 1
        return self.current_fps
