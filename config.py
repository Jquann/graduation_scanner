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
            'det_size': (256, 256),           # InsightFace detection size
            'detection_fps': 1,               # Face detection frequency (FPS)
            'display_fps': 25,                # Display frequency (FPS)
            'detection_frame_size': (320, 240), # Detection frame size
            'recognition_size': (112, 112),   # Face recognition input size
            'gui_update_ms': 40,              # GUI update interval (25 FPS)
            'match_cooldown': 1.0,            # Cooldown after each attempt (reduced)
            'face_buffer_size': 8,            # Face encoding buffer size
            'qr_timeout': 30.0,               # QR data timeout (30 seconds)
            'min_match_attempts': 3,          # Minimum attempts before giving up
            'max_match_attempts': 15,         # Maximum attempts before timeout
            'similarity_threshold_base': 0.35,
            'similarity_threshold_min': 0.28,
            'similarity_threshold_max': 0.45,
        },
        'balanced': {
            'det_size': (320, 320),
            'detection_fps': 2,
            'display_fps': 30,
            'detection_frame_size': (400, 300),
            'recognition_size': (112, 112),   # Face recognition input size
            'gui_update_ms': 33,
            'match_cooldown': 0.8,
            'face_buffer_size': 10,
            'qr_timeout': 45.0,               # 45 seconds for balanced mode
            'min_match_attempts': 5,
            'max_match_attempts': 25,
            'similarity_threshold_base': 0.35,
            'similarity_threshold_min': 0.28,
            'similarity_threshold_max': 0.45,
        },
        'high_performance': {
            'det_size': (512, 512),
            'detection_fps': 5,
            'display_fps': 30,
            'detection_frame_size': (640, 480),
            'recognition_size': (112, 112),   # Face recognition input size
            'gui_update_ms': 16,
            'match_cooldown': 0.5,
            'face_buffer_size': 12,
            'qr_timeout': 60.0,               # 60 seconds for high performance
            'min_match_attempts': 8,
            'max_match_attempts': 40,
            'similarity_threshold_base': 0.35,
            'similarity_threshold_min': 0.28,
            'similarity_threshold_max': 0.45,
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
    CONSECUTIVE_MATCHES_THRESHOLD = 2  # Need 2 consecutive matches to confirm
    FACE_ENCODING_EXPIRY = 3.0  # Keep encodings for 3 seconds
    ENCODING_BONUS = 0.01  # Per encoding bonus for threshold
    ATTEMPT_PENALTY = 0.005  # Per attempt penalty for threshold
    
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