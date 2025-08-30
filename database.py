#!/usr/bin/env python3
"""
Database management for student data persistence
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
import cv2
import qrcode
from PIL import Image

from config import Config
from models import Student


class StudentDatabase:
    """Manages student data storage and retrieval"""
    
    def __init__(self):
        self.data_file = Config.DATA_FILE
        self.photos_dir = Config.PHOTOS_DIR
        self.qrcodes_dir = Config.QRCODES_DIR
        self.students_data = self.load_students_data()
        
        # Ensure directories exist
        Config.create_directories()
    
    def load_students_data(self) -> Dict[str, List[Dict]]:
        """Load student data from file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading student data: {e}")
        return {"students": []}
    
    def save_students_data(self):
        """Save student data to file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.students_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving student data: {e}")
            return False
    
    def add_student(self, student: Student) -> bool:
        """Add a new student to the database"""
        # Check if student ID already exists
        if self.find_student_by_id(student.student_id):
            return False
        
        self.students_data["students"].append(student.to_dict())
        return self.save_students_data()
    
    def find_student_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Find student data by student ID"""
        for student in self.students_data["students"]:
            if student["student_id"] == student_id:
                return student
        return None
    
    def update_student(self, student_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update student data"""
        for i, student in enumerate(self.students_data["students"]):
            if student["student_id"] == student_id:
                self.students_data["students"][i].update(updated_data)
                return self.save_students_data()
        return False
    
    	
    def update_student_attendance(self, student_id: str) -> bool:
        """Update student's attendance status to Present"""
        for i, student in enumerate(self.students_data["students"]):
            if student["student_id"] == student_id:
                self.students_data["students"][i]["attendance"] = "Present"
                return self.save_students_data()
        return False
    
    def delete_student(self, student_id: str) -> bool:
        """Delete a student from the database"""
        original_count = len(self.students_data["students"])
        self.students_data["students"] = [
            s for s in self.students_data["students"] 
            if s["student_id"] != student_id
        ]
        
        if len(self.students_data["students"]) < original_count:
            # Also delete associated files
            self.delete_student_files(student_id)
            return self.save_students_data()
        return False
    
    def delete_student_files(self, student_id: str):
        """Delete student photo and QR code files"""
        try:
            photo_path = self.photos_dir / f"{student_id}.jpg"
            if photo_path.exists():
                photo_path.unlink()
            
            qr_path = self.qrcodes_dir / f"{student_id}.png"
            if qr_path.exists():
                qr_path.unlink()
        except Exception as e:
            print(f"Error deleting student files: {e}")
    
    def get_all_students(self) -> List[Dict[str, Any]]:
        """Get all students"""
        return self.students_data["students"]
    
    def get_student_count(self) -> int:
        """Get total number of students"""
        return len(self.students_data["students"])
    
    def save_student_photo(self, student_id: str, image) -> Optional[str]:
        """Save student photo and return path"""
        try:
            photo_filename = f"{student_id}.jpg"
            photo_path = self.photos_dir / photo_filename
            cv2.imwrite(str(photo_path), image)
            return str(photo_path)
        except Exception as e:
            print(f"Error saving student photo: {e}")
            return None
    
    def generate_qr_code(self, student_id: str) -> Optional[str]:
        """Generate QR code for student and return path"""
        try:
            qr = qrcode.QRCode(
                version=Config.QR_VERSION,
                box_size=Config.QR_BOX_SIZE,
                border=Config.QR_BORDER
            )
            qr.add_data(student_id)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_filename = f"{student_id}.png"
            qr_path = self.qrcodes_dir / qr_filename
            qr_img.save(qr_path)
            
            return str(qr_path)
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        students = self.get_all_students()
        
        # Count by graduation level
        graduation_levels = {}
        faculties = {}
        attendance_counts = {"Pending": 0, "Present": 0}
        
        for student in students:
            # Count graduation levels
            level = student.get('graduation_level', 'Unknown')
            graduation_levels[level] = graduation_levels.get(level, 0) + 1
            
            # Count faculties
            faculty = student.get('faculty', 'Unknown')
            faculties[faculty] = faculties.get(faculty, 0) + 1

            	
            # Count attendance status
            attendance = student.get('attendance', 'Pending')
            attendance_counts[attendance] = attendance_counts.get(attendance, 0) + 1

        return {
            'total_students': len(students),
            'graduation_levels': graduation_levels,
            'faculties': faculties
        }
    
    def search_students(self, query: str) -> List[Dict[str, Any]]:
        """Search students by name, ID, or faculty"""
        query = query.lower()
        results = []
        
        for student in self.students_data["students"]:
            if (query in student.get('student_id', '').lower() or
                query in student.get('name', '').lower() or
                query in student.get('faculty', '').lower()):
                results.append(student)
        
        return results
    
    def backup_database(self, backup_path: Optional[Path] = None) -> bool:
        """Create a backup of the database"""
        try:
            if backup_path is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = Config.DATA_DIR / f"backup_{timestamp}.json"
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.students_data, f, ensure_ascii=False, indent=2)
            
            print(f"Database backed up to: {backup_path}")
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def restore_database(self, backup_path: Path) -> bool:
        """Restore database from backup"""
        try:
            if not backup_path.exists():
                print(f"Backup file not found: {backup_path}")
                return False
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                self.students_data = json.load(f)
            
            return self.save_students_data()
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False