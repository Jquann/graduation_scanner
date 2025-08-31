#!/usr/bin/env python3
"""
QR code management functionality with database validation
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
    """Manages QR code operations with database validation"""
    
    def __init__(self, performance_config: dict, database=None):
        self.config = performance_config
        self.current_qr: Optional[QRData] = None
        self.database = database  # Database reference for validation
    
    def set_database(self, database):
        """Set database reference for QR validation"""
        self.database = database
    
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
        """Set the current QR data with validation and persistence tracking"""
        # First validate the QR code against database
        validation_result = self.validate_qr_data(data)
        
        if validation_result['is_valid']:
            self.current_qr = QRData(
                data=data.strip().upper(),  # Normalize the data
                source=source,
                load_time=time.time(),
                attempt_count=0,
                match_history=[]
            )
            print(f"✅ Valid QR code set: {data} from {source}")
        else:
            print(f"❌ Invalid QR code rejected: {validation_result['error_message']}")
            # Optionally, you might want to store invalid QR attempts for logging
            self.current_qr = None
    
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
    
    def validate_qr_data(self, data: str) -> dict:
        """
        Enhanced QR data validation with database checking
        
        Args:
            data (str): QR code data to validate
            
        Returns:
            dict: Validation result with detailed information
        """
        # Basic format validation
        if not data or len(data.strip()) == 0:
            return {
                'is_valid': False,
                'error_message': 'QR code is empty',
                'error_type': 'EMPTY_QR',
                'student_data': None
            }
        
        # Length check (assuming student ID has reasonable length limits)
        data = data.strip()
        if len(data) < 3 or len(data) > 20:  # Adjust as needed
            return {
                'is_valid': False,
                'error_message': f'QR code length invalid ({len(data)} characters)',
                'error_type': 'INVALID_LENGTH',
                'student_data': None
            }
        
        # Database validation if database is available
        if self.database:
            db_validation = self.database.validate_qr_code(data)
            return db_validation
        else:
            # Fallback validation without database
            print("⚠️ Database not available for QR validation")
            return {
                'is_valid': True,  # Assume valid if no database
                'error_message': None,
                'error_type': None,
                'student_data': None
            }
    
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
                'is_max_attempts': False,
                'validation_status': 'NO_QR'
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
            'match_history': self.current_qr.match_history,
            'validation_status': 'VALID'
        }
    
    def get_validation_error_message(self, error_type: str) -> str:
        """Get user-friendly error messages for different validation errors"""
        error_messages = {
            'EMPTY_QR': 'Please scan a valid QR code',
            'INVALID_LENGTH': 'QR code format is invalid',
            'STUDENT_NOT_FOUND': 'Student not found in database. Please check the QR code.',
            'DATABASE_ERROR': 'Database error occurred during validation'
        }
        return error_messages.get(error_type, 'Unknown validation error')
    
    def draw_qr_overlay(self, frame: np.ndarray, qr_codes: List[Tuple[str, List[int]]]):
        """Draw QR code overlays on frame with bounding boxes and validation status"""
        for qr_data, bbox in qr_codes:
            # Validate QR code
            validation = self.validate_qr_data(qr_data)
            
            # Choose color based on validation
            if validation['is_valid']:
                color = (0, 255, 0)  # Green for valid
                status = "✅ Valid"
            else:
                color = (0, 0, 255)  # Red for invalid
                status = f"❌ {validation['error_type']}"
            
            # Draw bounding box
            x1, y1, x2, y2 = bbox
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Add QR data text
            cv2.putText(frame, f"QR: {qr_data}", (x1, y1 - 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Add validation status
            cv2.putText(frame, status, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame