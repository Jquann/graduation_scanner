#!/usr/bin/env python3
"""
QR code management functionality
"""

import cv2
import qrcode
from pyzbar import pyzbar
from typing import Optional, List, Tuple
import time
from PIL import Image
import numpy as np
from config import Config
from models import QRData


class QRCodeManager:
    """Manages QR code operations"""
    
    def __init__(self, performance_config: dict):
        self.config = performance_config
        self.current_qr: Optional[QRData] = None
    
    def generate_qr_code(self, data: str, save_path: Optional[str] = None) -> Image.Image:
        """Generate a QR code image"""
        qr = qrcode.QRCode(
            version=Config.QR_VERSION,
            box_size=Config.QR_BOX_SIZE,
            border=Config.QR_BORDER,
            error_correction=qrcode.constants.ERROR_CORRECT_L
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        if save_path:
            img.save(save_path)
        
        return img
    
    def decode_qr_from_image(self, image_path: str) -> Optional[str]:
        """Decode QR code from an image file"""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Decode QR codes
            barcodes = pyzbar.decode(image)
            
            if not barcodes:
                return None
            
            if len(barcodes) > 1:
                print(f"Multiple QR codes found ({len(barcodes)}), using the first one")
            
            # Get first QR code data
            qr_data = barcodes[0].data.decode('utf-8')
            return qr_data
            
        except Exception as e:
            print(f"Error decoding QR from image: {e}")
            return None
    
    def decode_qr_from_frame(self, frame: np.ndarray) -> List[str]:
        """Decode all QR codes from a video frame"""
        try:
            barcodes = pyzbar.decode(frame)
            qr_codes = []
            
            for barcode in barcodes:
                qr_data = barcode.data.decode('utf-8')
                qr_codes.append(qr_data)
            
            return qr_codes
            
        except Exception as e:
            print(f"Error decoding QR from frame: {e}")
            return []
    
    def set_current_qr(self, data: str, source: str):
        """Set the current QR data with persistence tracking"""
        self.current_qr = QRData(
            data=data,
            source=source,
            load_time=time.time(),
            attempt_count=0,
            match_history=[]
        )
    
    def clear_current_qr(self):
        """Clear the current QR data"""
        self.current_qr = None
    
    def get_current_qr(self) -> Optional[QRData]:
        """Get the current QR data"""
        return self.current_qr
    
    def is_qr_expired(self) -> bool:
        """Check if current QR has expired"""
        if not self.current_qr:
            return True
        
        return self.current_qr.is_expired(self.config['qr_timeout'])
    
    def get_qr_remaining_time(self) -> float:
        """Get remaining time for current QR"""
        if not self.current_qr:
            return 0.0
        
        return self.current_qr.get_remaining_time(self.config['qr_timeout'])
    
    def increment_attempt(self):
        """Increment attempt counter for current QR"""
        if self.current_qr:
            self.current_qr.increment_attempt()
    
    def get_attempt_count(self) -> int:
        """Get current attempt count"""
        if self.current_qr:
            return self.current_qr.attempt_count
        return 0
    
    def is_max_attempts_reached(self) -> bool:
        """Check if maximum attempts have been reached"""
        if not self.current_qr:
            return False
        
        return self.current_qr.attempt_count >= self.config['max_match_attempts']
    
    def reset_attempts(self):
        """Reset attempt counter without clearing QR data"""
        if self.current_qr:
            self.current_qr.attempt_count = 0
            self.current_qr.match_history.clear()
    
    def add_match_attempt(self, similarity: float, avg_similarity: float,
                         threshold: float, success: bool):
        """Record a match attempt"""
        if self.current_qr:
            self.current_qr.add_match_attempt(
                similarity, avg_similarity, threshold, success
            )
    
    def get_match_history(self) -> List[dict]:
        """Get match history for current QR"""
        if self.current_qr:
            return self.current_qr.match_history
        return []
    
    def validate_qr_data(self, data: str) -> bool:
        """Validate QR data format"""
        # Add validation logic based on your requirements
        # For example, check if it's a valid student ID format
        if not data or len(data) == 0:
            return False
        
        # Add more validation rules as needed
        return True
    
    def get_qr_status_info(self) -> dict:
        """Get comprehensive QR status information"""
        if not self.current_qr:
            return {
                'has_qr': False,
                'data': None,
                'source': None,
                'elapsed_time': 0,
                'remaining_time': 0,
                'attempt_count': 0,
                'max_attempts': self.config['max_match_attempts'],
                'is_expired': True,
                'is_max_attempts': False
            }
        
        elapsed = time.time() - self.current_qr.load_time
        remaining = self.get_qr_remaining_time()
        
        return {
            'has_qr': True,
            'data': self.current_qr.data,
            'source': self.current_qr.source,
            'elapsed_time': elapsed,
            'remaining_time': remaining,
            'attempt_count': self.current_qr.attempt_count,
            'max_attempts': self.config['max_match_attempts'],
            'is_expired': self.is_qr_expired(),
            'is_max_attempts': self.is_max_attempts_reached(),
            'match_history': self.current_qr.match_history
        }
    
    def draw_qr_overlay(self, frame: np.ndarray, qr_codes: List[Tuple[str, List[int]]]):
        """Draw QR code overlays on frame with bounding boxes"""
        for qr_data, bbox in qr_codes:
            # Draw bounding box
            x1, y1, x2, y2 = bbox
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Add QR data text
            cv2.putText(frame, f"QR: {qr_data}", (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return frame