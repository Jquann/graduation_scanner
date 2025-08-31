#!/usr/bin/env python3
"""
Configuration management for Graduation Scanner
Contains all configurable parameters and settings
"""

from pathlib import Path


class Config:
    """Central configuration class"""
    
    # Application info
    APP_NAME = "Graduation Ceremony Recognition System"
    APP_VERSION = "1.0.0"
    
    # Data storage paths
    DATA_DIR = Path("graduation_data")
    PHOTOS_DIR = DATA_DIR / "photos"
    QRCODES_DIR = DATA_DIR / "qrcodes"
    DATA_FILE = DATA_DIR / "students_data.json"
    
    # GUI settings
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    CAMERA_DISPLAY_SIZE = (640, 480)
    PHOTO_PREVIEW_SIZE = (300, 300)
    
    # Face recognition settings
    INSIGHTFACE_PROVIDER = 'CPUExecutionProvider'
    
    # Performance configurations
    PERFORMANCE_CONFIGS = {
        'low_cpu': {
            'det_size': (320, 320),
            'detection_fps': 1,
            'display_fps': 25,
            'detection_frame_size': (400, 300),
            'recognition_size': (112, 112),
            'gui_update_ms': 40,
            'match_cooldown': 0.8,
            'face_buffer_size': 12,
            'qr_timeout': 30.0,
            'min_match_attempts': 2,
            'max_match_attempts': 20,
            'similarity_threshold_base': 0.28,
            'similarity_threshold_min': 0.22,
            'similarity_threshold_max': 0.38,
        },
        'balanced': {
            'det_size': (480, 480),
            'detection_fps': 2,
            'display_fps': 30,
            'detection_frame_size': (480, 360),
            'recognition_size': (112, 112),
            'gui_update_ms': 33,
            'match_cooldown': 0.6,
            'face_buffer_size': 15,
            'qr_timeout': 45.0,
            'min_match_attempts': 3,
            'max_match_attempts': 30,
            'similarity_threshold_base': 0.28,
            'similarity_threshold_min': 0.22,
            'similarity_threshold_max': 0.38,
        },
        'high_performance': {
            'det_size': (640, 640),
            'detection_fps': 5,
            'display_fps': 30,
            'detection_frame_size': (640, 480),
            'recognition_size': (112, 112),
            'gui_update_ms': 16,
            'match_cooldown': 0.4,
            'face_buffer_size': 18,
            'qr_timeout': 60.0,
            'min_match_attempts': 5,
            'max_match_attempts': 40,
            'similarity_threshold_base': 0.28,
            'similarity_threshold_min': 0.22,
            'similarity_threshold_max': 0.38,
        }
    }
    
    # Camera settings
    CAMERA_INDEX = 0
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    
    # QR Code settings
    QR_VERSION = 1
    QR_BOX_SIZE = 10
    QR_BORDER = 5
    
    # Recognition settings
    CONSECUTIVE_MATCHES_THRESHOLD = 2
    FACE_ENCODING_EXPIRY = 3.0
    ENCODING_BONUS = 0.008
    ATTEMPT_PENALTY = 0.005
    
    # Graduation levels
    GRADUATION_LEVELS = [
        'Pass',
        'With Merit',
        'With Distinction',
        'With Distinction and Book Prize'
    ]
    
    @classmethod
    def get_performance_config(cls, mode='balanced'):
        """Get performance configuration by mode"""
        return cls.PERFORMANCE_CONFIGS.get(mode, cls.PERFORMANCE_CONFIGS['balanced'])
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        for dir_path in [cls.DATA_DIR, cls.PHOTOS_DIR, cls.QRCODES_DIR]:
            dir_path.mkdir(exist_ok=True)