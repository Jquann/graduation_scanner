#!/usr/bin/env python3
"""
Camera worker and threading management
"""

import cv2
import threading
import queue
import time
import numpy as np
from typing import Optional, Callable, Any
from datetime import datetime
from PIL import Image, ImageTk

from config import Config
from models import FaceDetectionResult, PerformanceStats


class CameraWorker:
    """Manages camera capture and face detection threads"""
    
    def __init__(self, face_engine, qr_manager, performance_config):
        self.face_engine = face_engine
        self.qr_manager = qr_manager
        self.config = performance_config
        
        # Queues for inter-thread communication
        self.face_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.face_detection_queue = queue.Queue()
        
        # Thread control
        self.is_running = False
        self.camera_thread = None
        self.result_thread = None
        
        # Performance tracking
        self.performance_stats = PerformanceStats()
        
        # Camera instance
        self.cap = None
        
        # Detection state
        self.current_faces = []
        
        # Callbacks
        self.on_match_found = None
        self.on_status_update = None
    
    def start(self):
        """Start camera and processing threads"""
        if self.is_running:
            return False
        
        self.is_running = True
        
        # Clear all queues
        self._clear_queues()
        
        # Reset performance stats
        self.performance_stats = PerformanceStats()
        
        # Start threads
        self.camera_thread = threading.Thread(target=self._camera_worker, daemon=True)
        self.camera_thread.start()
        
        self.result_thread = threading.Thread(target=self._result_worker, daemon=True)
        self.result_thread.start()
        
        return True
    
    def stop(self):
        """Stop camera and processing threads"""
        self.is_running = False
        
        # Wait for threads to finish
        if self.camera_thread:
            self.camera_thread.join(timeout=2.0)
        if self.result_thread:
            self.result_thread.join(timeout=2.0)
        
        # Release camera
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Clear queues
        self._clear_queues()
    
    def _clear_queues(self):
        """Clear all queues"""
        for q in [self.face_queue, self.result_queue, self.face_detection_queue]:
            while not q.empty():
                try:
                    q.get_nowait()
                except queue.Empty:
                    break
    
    def _camera_worker(self):
        """Camera capture and face detection worker thread"""
        self.cap = cv2.VideoCapture(Config.CAMERA_INDEX)
        
        if not self.cap.isOpened():
            self.result_queue.put(("error", "Cannot open camera"))
            return
        
        # Set camera parameters
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, Config.CAMERA_FPS)
        
        # Timing variables
        last_detection_time = 0
        detection_interval = 1.0 / self.config['detection_fps']
        display_interval = 1.0 / self.config['display_fps']
        last_display_time = time.time()
        
        detector = cv2.QRCodeDetector()

        while self.is_running:
            current_time = time.time()
            ret, frame = self.cap.read()
            
            if not ret:
                time.sleep(0.01)
                continue
            
            frame = cv2.flip(frame, 1)  # Mirror flip
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            qr_data, points, _ = detector.detectAndDecode(frame_rgb)
            if qr_data:
                self.qr_manager.set_current_qr(qr_data, "Camera Scan")
                self.result_queue.put(("qr_scanned", qr_data))
            
            # Face detection (low frequency)
            should_detect = (
                current_time - last_detection_time > detection_interval and
                self.qr_manager.get_current_qr() is not None
            )
            
            if should_detect:
                self._async_face_detection(frame_rgb.copy(), current_time)
                last_detection_time = current_time
            
            # Prepare display frame
            display_frame = self._prepare_display_frame(frame_rgb, current_time)
            
            # Control display frequency
            if current_time - last_display_time >= display_interval:
                # Convert to GUI format
                pil_image = Image.fromarray(display_frame)
                pil_image = pil_image.resize(Config.CAMERA_DISPLAY_SIZE)
                photo = ImageTk.PhotoImage(pil_image)
                
                self.result_queue.put(("camera_frame", photo))
                last_display_time = current_time
            
            # Process face detection results
            self._process_detection_results()
            
            # Update performance stats
            self.performance_stats.update_fps()
            
            time.sleep(0.01)
        
    
    def _async_face_detection(self, frame: np.ndarray, timestamp: float):
        """Perform asynchronous face detection"""
        def detect():
            try:
                # Resize frame for detection
                detection_frame = cv2.resize(frame, self.config['detection_frame_size'])
                
                # Detect faces
                faces = self.face_engine.detect_faces(detection_frame)
                
                # Scale coordinates back
                scale_x = Config.CAMERA_WIDTH / self.config['detection_frame_size'][0]
                scale_y = Config.CAMERA_HEIGHT / self.config['detection_frame_size'][1]
                
                faces_info = []
                for face in faces:
                    bbox = face.bbox.astype(int)
                    scaled_bbox = [
                        int(bbox[0] * scale_x),
                        int(bbox[1] * scale_y),
                        int(bbox[2] * scale_x),
                        int(bbox[3] * scale_y)
                    ]
                    
                    # Process face with spoofing check
                    processed_result = self.face_engine.process_single_face_with_spoofing(face, frame)
                    
                    is_real = True
                    spoof_confidence = 0.0
                    if processed_result:
                        embedding, is_real, spoof_confidence = processed_result
                        if is_real:
                            self.face_queue.put(embedding)
                        else:
                            print(f"Spoofing detected for a face with confidence: {spoof_confidence:.2f}")
                            self.face_queue.put("SPOOF_DETECTED") # Signal spoof detection
                    else:
                        # If processing returns None, it means spoofing was detected or an error occurred
                        is_real = False
                        print("Face processing (including spoofing check) returned None.")
                        self.face_queue.put("SPOOF_DETECTED") # Signal general processing failure

                    face_info = FaceDetectionResult(
                        bbox=scaled_bbox,
                        confidence=getattr(face, 'det_score', 1.0),
                        timestamp=timestamp,
                        is_spoof=not is_real # Set is_spoof based on processing result
                    )
                    faces_info.append(face_info)

                # Update current faces
                self.face_detection_queue.put({
                    'type': 'faces_detected',
                    'faces': faces_info,
                    'timestamp': timestamp
                })
                
            except Exception as e:
                print(f"Async face detection error: {e}")
        
        # Start detection in separate thread
        threading.Thread(target=detect, daemon=True).start()
    
    def _prepare_display_frame(self, frame: np.ndarray, current_time: float) -> np.ndarray:
        """Prepare frame for display with overlays"""
        display_frame = frame.copy()
        
        # Draw face boxes
        for face in self.current_faces:
            bbox = face.bbox
            
            # Determine color and text based on spoofing status
            if face.is_spoof:
                box_color = (0, 0, 255) # Red for spoof
                text_label = "Spoof Detected!"
            else:
                box_color = (0, 255, 0) # Green for real face
                text_label = f"Face: {face.confidence:.2f}"
            
            cv2.rectangle(display_frame, (bbox[0], bbox[1]), 
                         (bbox[2], bbox[3]), box_color, 2)
            
            # Add text label
            cv2.putText(display_frame, text_label,
                       (bbox[0], bbox[1]-10), cv2.FONT_HERSHEY_SIMPLEX,
                       0.6, box_color, 2)
        
        # Add status overlay
        self._add_status_overlay(display_frame, current_time)
        
        return display_frame
    
    def _add_status_overlay(self, frame: np.ndarray, current_time: float):
        """Add status information overlay"""
        height, width = frame.shape[:2]
        
        # Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # QR status
        qr_status = self.qr_manager.get_qr_status_info()
        
        # Status text
        status_lines = [
            f"Faces: {len(self.current_faces)}",
            f"QR: {qr_status['data'] if qr_status['has_qr'] else 'None'}",
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        ]
        
        for i, line in enumerate(status_lines):
            y_pos = 25 + (i * 20)
            cv2.putText(frame, line, (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # QR timeout indicator
        if qr_status['has_qr']:
            remaining = qr_status['remaining_time']
            color = (0, 255, 255) if remaining > 10 else (0, 0, 255)
            cv2.putText(frame, f"QR Timeout: {int(remaining)}s",
                       (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # FPS indicator
        cv2.putText(frame, f"FPS: {self.performance_stats.current_fps}",
                   (width - 100, 25), cv2.FONT_HERSHEY_SIMPLEX,
                   0.6, (0, 255, 0), 2)
    
    def _process_detection_results(self):
        """Process face detection results from queue"""
        try:
            while True:
                result = self.face_detection_queue.get_nowait()
                if result['type'] == 'faces_detected':
                    self.current_faces = result['faces']
                    self.performance_stats.detection_count += 1
        except queue.Empty:
            pass
    
    def _result_worker(self):
        """Result processing worker thread"""
        from face_matching import FaceMatcher
        matcher = FaceMatcher(self.face_engine, self.qr_manager, self.config)
        
        while self.is_running:
            # Process face encodings for matching
            matcher.process_encodings(self.face_queue, self.result_queue)
            
            # Check QR timeout
            if self.qr_manager.is_qr_expired():
                if self.qr_manager.get_current_qr():
                    self.result_queue.put(("qr_timeout", self.qr_manager.get_qr_status_info()))
                    self.qr_manager.clear_current_qr()
            
            time.sleep(0.1)
    
    def get_performance_stats(self) -> dict:
        """Get performance statistics"""
        return {
            'fps': self.performance_stats.current_fps,
            'detections': self.performance_stats.detection_count,
            'recognitions': self.performance_stats.recognition_count
        }
    
    def capture_photo(self) -> Optional[np.ndarray]:
        """Capture a single photo from camera"""
        if not self.cap or not self.cap.isOpened():
            temp_cap = cv2.VideoCapture(Config.CAMERA_INDEX)
            if not temp_cap.isOpened():
                return None
            
            ret, frame = temp_cap.read()
            temp_cap.release()
        else:
            ret, frame = self.cap.read()
        
        if ret:
            return cv2.flip(frame, 1)
        return None
