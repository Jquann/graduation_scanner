#!/usr/bin/env python3
"""
This module implements the core face matching logic for recognition.
It handles collecting face encodings, comparing them against a student database,
and managing the matching state based on QR code data and recognition attempts.
"""

import time
import queue
import numpy as np
from typing import List, Optional
from datetime import datetime
import pyttsx3 # Import the text-to-speech library
import threading # Import threading for the TTS worker

from models import RecognitionResult
from database import StudentDatabase


class FaceMatcher:
    """
    Manages the face matching process, including buffering face encodings,
    performing similarity calculations, and determining successful matches
    based on dynamic thresholds and consecutive match criteria.
    """
    
    def __init__(self, face_engine, qr_manager, config):
        """
        Initializes the FaceMatcher with necessary dependencies.

        Args:
            face_engine: An instance of FaceRecognitionEngine for face operations.
            qr_manager: An instance of QRManager for handling QR code data and attempts.
            config: Configuration settings for face matching parameters.
        """
        self.face_engine = face_engine
        self.qr_manager = qr_manager
        self.config = config
        self.database = StudentDatabase() # Initialize the student database connection
        
        # State variables for managing the matching process
        self.face_encodings_buffer = [] # Stores recent face encodings
        self.last_match_time = 0        # Timestamp of the last matching attempt
        self.consecutive_matches = 0    # Counter for consecutive successful matches
        self.tts_queue = queue.Queue() # Queue for TTS commands
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True) # TTS worker thread
        self.tts_thread.start()
    
    def process_encodings(self, face_queue: queue.Queue, result_queue: queue.Queue):
        """
        Main processing loop for face encodings.
        It collects new encodings, cleans expired ones, and triggers matching if conditions are met.

        Args:
            face_queue (queue.Queue): Queue from which to retrieve new face encodings.
            result_queue (queue.Queue): Queue to put recognition results (matches, errors).
        """
        current_time = time.time()
        
        # Step 1: Collect new face encodings from the input queue
        self._collect_encodings(face_queue, current_time)
        
        # Step 2: Remove encodings that have expired from the buffer
        self._clean_expired_encodings(current_time)
        
        # Step 3: Check if conditions are met to perform a matching operation
        if self._should_perform_matching(current_time):
            self._perform_matching(result_queue, current_time)
    
    def _collect_encodings(self, face_queue: queue.Queue, current_time: float):
        """
        Collects face encodings from the provided queue and adds them to the buffer.
        Maintains the buffer size according to configuration.

        Args:
            face_queue (queue.Queue): The queue containing incoming face encodings.
            current_time (float): The current timestamp for marking collected encodings.
        """
        try:
            # Continuously retrieve encodings until the queue is empty
            while True:
                face_encoding = face_queue.get_nowait() # Non-blocking retrieval
                self.face_encodings_buffer.append({
                    'encoding': face_encoding,
                    'timestamp': current_time
                })
                
                # Ensure the buffer does not exceed the configured maximum size
                if len(self.face_encodings_buffer) > self.config['face_buffer_size']:
                    self.face_encodings_buffer.pop(0) # Remove the oldest encoding
        except queue.Empty:
            # Expected exception when the queue is empty, no action needed
            pass
    
    def _clean_expired_encodings(self, current_time: float):
        """
        Removes face encodings from the buffer that have exceeded their retention time.

        Args:
            current_time (float): The current timestamp to compare against encoding timestamps.
        """
        # Filter out encodings older than 3 seconds (configurable via config if needed)
        self.face_encodings_buffer = [
            item for item in self.face_encodings_buffer
            if current_time - item['timestamp'] < 3.0  # Keep for 3 seconds
        ]
    
    def _should_perform_matching(self, current_time: float) -> bool:
        """
        Determines if a face matching operation should be performed based on
        the presence of QR data, available face encodings, attempt limits, and cooldown.

        Args:
            current_time (float): The current timestamp.

        Returns:
            bool: True if matching should proceed, False otherwise.
        """
        qr_data = self.qr_manager.get_current_qr()
        
        # Matching requires an active QR code
        if not qr_data:
            return False
        
        # Matching requires at least one face encoding in the buffer
        if not self.face_encodings_buffer:
            return False
        
        # Do not perform matching if maximum attempts for the current QR are reached
        if self.qr_manager.is_max_attempts_reached():
            return False
        
        # Check if the cooldown period since the last match attempt has passed
        cooldown_passed = (current_time - self.last_match_time) > self.config['match_cooldown']
        
        return cooldown_passed
    
    def _perform_matching(self, result_queue: queue.Queue, current_time: float):
        """
        Executes the face matching process against the student database.
        It retrieves student data, calculates similarity, applies dynamic thresholds,
        and reports results to the result queue.

        Args:
            result_queue (queue.Queue): Queue to put recognition results.
            current_time (float): The current timestamp for logging and cooldown.
        """
        qr_data = self.qr_manager.get_current_qr()
        if not qr_data:
            return # Should not happen if _should_perform_matching was True
        
        # Find the student in the database using the QR code data (student ID)
        student = self.database.find_student_by_id(qr_data.data)
        
        if not student:
            # If student is not found, report it and increment attempt count
            if self.qr_manager.get_attempt_count() == 0:
                self.qr_manager.increment_attempt()
                result_queue.put(("student_not_found", {
                    "student_id": qr_data.data,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }))
            self.last_match_time = current_time # Update last match time to respect cooldown
            return
        
        # Increment the attempt counter for the current QR code
        self.qr_manager.increment_attempt()
        
        # Get the most recent encodings from the buffer for comparison
        recent_encodings = [
            item['encoding'] for item in self.face_encodings_buffer[-5:] # Use last 5 encodings
        ]
        
        if not recent_encodings:
            return # No recent encodings to compare
        
        # Prepare the target encoding from the student's stored face data
        target_encoding = np.array(student["face_encoding"])
        # Calculate batch similarity using the face engine
        best_similarity, avg_similarity = self.face_engine.calculate_batch_similarity(
            recent_encodings, target_encoding
        )
        
        # Calculate a dynamic threshold based on the number of encodings and attempts
        dynamic_threshold = self.face_engine.calculate_dynamic_threshold(
            len(recent_encodings),
            self.qr_manager.get_attempt_count(),
            self.config.get('similarity_threshold_base', 0.35)
        )
        
        # Log the attempt details for debugging and monitoring
        print(f"Attempt {self.qr_manager.get_attempt_count()}: {student['name']} - "
              f"Best={best_similarity:.3f}, Avg={avg_similarity:.3f}, "
              f"Threshold={dynamic_threshold:.3f}")
        
        # Record the details of this matching attempt
        self.qr_manager.add_match_attempt(
            best_similarity, avg_similarity, dynamic_threshold,
            best_similarity > dynamic_threshold
        )
        
        # Check if the best similarity exceeds the dynamic threshold
        if best_similarity > dynamic_threshold:
            self.consecutive_matches += 1 # Increment consecutive match count
            
            # If enough consecutive matches are achieved, confirm a successful match
            if self.consecutive_matches >= 2:  # Config.CONSECUTIVE_MATCHES_THRESHOLD (hardcoded to 2 for now)
                # Create a RecognitionResult object for the successful match
                result = RecognitionResult(
                    student_id=student["student_id"],
                    name=student["name"],
                    faculty=student["faculty"],
                    graduation_level=student["graduation_level"],
                    similarity=best_similarity,
                    avg_similarity=avg_similarity,
                    confidence_level=min(self.consecutive_matches, 5), # Cap confidence at 5
                    total_attempts=self.qr_manager.get_attempt_count()
                )
                
                # Put the successful match result into the queue
                result_queue.put(("match_found", result.to_display_dict()))
                
                # Announce the recognized student's name
                self._announce_name(student["name"])

                # Reset state for the next QR code recognition
                self.face_encodings_buffer.clear()
                self.consecutive_matches = 0
                self.qr_manager.clear_current_qr() # Clear current QR data to await a new one
        else:
            # If similarity is not enough, reset consecutive matches
            self.consecutive_matches = 0
            
            # Report low similarity if below minimum attempts and similarity is above a minimal value
            if self.qr_manager.get_attempt_count() < self.config['min_match_attempts']:
                if best_similarity > 0.2: # Only report if there's some minimal similarity
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
        
        self.last_match_time = current_time # Update last match time after processing
    
    def force_match(self, student_id: str) -> Optional[RecognitionResult]:
        """
        Forces a manual match for a student, bypassing the normal recognition process.
        This is typically used for administrative overrides or testing.

        Args:
            student_id (str): The ID of the student to force match.

        Returns:
            Optional[RecognitionResult]: A RecognitionResult object if the student is found,
                                        otherwise None.
        """
        student = self.database.find_student_by_id(student_id)
        
        if not student:
            return None # Student not found in the database
        
        # Create a RecognitionResult object with overridden values for a forced match
        result = RecognitionResult(
            student_id=student["student_id"],
            name=student["name"],
            faculty=student["faculty"],
            graduation_level=student["graduation_level"],
            similarity=1.0,         # Set to 1.0 for a perfect match
            avg_similarity=1.0,     # Set to 1.0 for a perfect match
            confidence_level=5,     # Highest confidence
            total_attempts=0,       # No attempts made through normal process
            manual_override=True    # Flag indicating a manual override
        )
        
        return result
    
    def _initialize_tts_engine(self):
        """
        Initializes the text-to-speech engine.
        """
        engine = pyttsx3.init()
        # You can configure properties like voice, rate, and volume here
        # For example:
        # voices = engine.getProperty('voices')
        # engine.setProperty('voice', voices[0].id) # Change index for different voices
        # engine.setProperty('rate', 150) # Speed of speech
        # engine.setProperty('volume', 0.9) # Volume (0.0 to 1.0)
        print("TTS engine initialized.")
        return engine

    def _announce_name(self, name: str):
        """
        Makes a voice announcement of the recognized name.
        """
        print(f"Announcing: Welcome, {name}") # Added print statement for verification
        self.tts_queue.put(f"Welcome, {name}")

    def _tts_worker(self):
        """Dedicated worker thread for text-to-speech announcements."""
        while True:
            message = self.tts_queue.get() # Blocks until an item is available
            if message is None: # Sentinel value to stop the thread
                break
            print(f"Announcing: {message}") # Print for verification
            pyttsx3.speak(message)
            self.tts_queue.task_done()

    def reset_state(self):
        # Stop the TTS thread when resetting state or application shutdown
        self.tts_queue.put(None) # Send sentinel to stop the thread
        self.tts_thread.join(timeout=1.0) # Wait for the thread to finish
        """
        Resets the internal matching state variables.
        This is typically called when a new QR code is scanned or after a successful match
        to prepare for the next recognition cycle.
        """
        self.face_encodings_buffer.clear() # Clear all buffered encodings
        self.consecutive_matches = 0    # Reset consecutive match count
        self.last_match_time = 0        # Reset last match time