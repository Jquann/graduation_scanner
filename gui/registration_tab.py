#!/usr/bin/env python3
"""
Student registration tab GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import os
import re
from datetime import datetime
from PIL import Image, ImageTk

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from models import Student


class RegistrationTab:
    """Student registration interface"""
    
    def __init__(self, parent, face_engine, database):
        self.face_engine = face_engine
        self.database = database
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Initialize variables
        self.student_id_var = tk.StringVar()
        self.student_name_var = tk.StringVar()
        self.faculty_var = tk.StringVar()
        self.graduation_level_var = tk.StringVar()
        self.photo_path = None
        
        self.setup_ui()
    
    def validate_student_id(self, student_id):
        """
        Validate student ID format: 11AAA11111
        - 2 digits
        - 3 uppercase letters  
        - 5 digits
        """
        pattern = r'^[0-9]{2}[A-Z]{3}[0-9]{5}$'
        return re.match(pattern, student_id) is not None
    
    def setup_ui(self):
        """Setup registration UI"""
        # Left side: Form
        form_frame = ttk.LabelFrame(self.frame, text="Student Information")
        form_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Student ID
        ttk.Label(form_frame, text="Student ID:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        id_entry = ttk.Entry(form_frame, textvariable=self.student_id_var, width=30)
        id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Add format hint for student ID
        id_hint = ttk.Label(form_frame, text="Format: 11AAA11111 (2 digits + 3 letters + 5 digits)", 
                           foreground="gray", font=('Arial', 8))
        id_hint.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        
        # Name
        ttk.Label(form_frame, text="Full Name:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.student_name_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Faculty
        ttk.Label(form_frame, text="Faculty/Department:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.faculty_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        # Graduation Level
        ttk.Label(form_frame, text="Graduation Level:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        level_combo = ttk.Combobox(form_frame, textvariable=self.graduation_level_var, width=27)
        level_combo['values'] = Config.GRADUATION_LEVELS
        level_combo.grid(row=3, column=1, padx=5, pady=5)
        
        # Photo selection
        photo_frame = ttk.Frame(form_frame)
        photo_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(photo_frame, text="📁 Choose Photo", command=self.select_photo).pack(side='left', padx=5)
        ttk.Button(photo_frame, text="📷 Take Photo", command=self.capture_photo).pack(side='left', padx=5)
        
        self.photo_label = ttk.Label(form_frame, text="No photo selected")
        self.photo_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Registration buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="✅ Register Student", 
                  command=self.register_student).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🔄 Clear Form", 
                  command=self.clear_form).pack(side='left', padx=5)
        
        # Right side: Photo preview
        preview_frame = ttk.LabelFrame(self.frame, text="Photo Preview")
        preview_frame.pack(side='right', fill='y', padx=5, pady=5)
        
        self.photo_preview = ttk.Label(preview_frame, text="Photo Preview\n(300x300)")
        self.photo_preview.pack(padx=20, pady=20)
        
        # Set focus to first entry
        id_entry.focus_set()
    
    def select_photo(self):
        """Select photo file"""
        file_path = filedialog.askopenfilename(
            title="Select Student Photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            # Verify face in photo
            if not self.face_engine.verify_face_in_image(file_path):
                messagebox.showwarning("Warning", "No face detected in selected photo. Please choose another photo.")
                return
            
            self.photo_path = file_path
            self.photo_label.config(text=f"Selected: {os.path.basename(file_path)}")
            self.update_photo_preview()
    
    def capture_photo(self):
        """Open camera capture window"""
        capture_window = PhotoCaptureWindow(self.frame, self.face_engine)
        self.frame.wait_window(capture_window.window)
        
        if capture_window.captured_photo_path:
            self.photo_path = capture_window.captured_photo_path
            self.photo_label.config(text=f"Captured: {os.path.basename(self.photo_path)}")
            self.update_photo_preview()
    
    def update_photo_preview(self):
        """Update photo preview"""
        if self.photo_path and os.path.exists(self.photo_path):
            try:
                image = Image.open(self.photo_path)
                image = image.resize(Config.PHOTO_PREVIEW_SIZE)
                photo = ImageTk.PhotoImage(image)
                self.photo_preview.configure(image=photo)
                self.photo_preview.image = photo
            except Exception as e:
                print(f"Error previewing photo: {e}")
    
    def cleanup_temp_file(self, file_path):
        """Clean up temporary file"""
        try:
            if file_path and os.path.exists(file_path) and file_path.startswith('temp_'):
                os.remove(file_path)
                print(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            print(f"Warning: Could not clean up temporary file {file_path}: {e}")
    
    def register_student(self):
        """Register new student"""
        # Validate input
        student_id = self.student_id_var.get().strip().upper()  # Convert to uppercase
        student_name = self.student_name_var.get().strip()
        faculty = self.faculty_var.get().strip()
        graduation_level = self.graduation_level_var.get().strip()
        
        if not all([student_id, student_name, faculty, graduation_level]):
            messagebox.showerror("Error", "Please fill in all required information")
            return
        
        # Validate student ID format
        if not self.validate_student_id(student_id):
            messagebox.showerror("Error", 
                               "Invalid Student ID format!\n\n" +
                               "Required format: 11AAA11111\n" +
                               "Example: 22CSC12345\n\n" +
                               "• 2 digits (year/batch)\n" +
                               "• 3 uppercase letters (program code)\n" +
                               "• 5 digits (sequential number)")
            return
        
        if not self.photo_path or not os.path.exists(self.photo_path):
            messagebox.showerror("Error", "Please select or take a student photo")
            return
        
        # Check if student ID already exists
        if self.database.find_student_by_id(student_id):
            messagebox.showerror("Error", f"Student ID '{student_id}' already exists!\nPlease use a different ID.")
            return
        
        temp_file_to_cleanup = None
        try:
            # Check if this is a temporary captured photo
            if self.photo_path and self.photo_path.startswith('temp_'):
                temp_file_to_cleanup = self.photo_path
            
            # Process face image
            image = cv2.imread(self.photo_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Extract face encoding
            face_encoding = self.face_engine.extract_face_encoding(image_rgb)
            if face_encoding is None:
                messagebox.showerror("Error", "No face detected in photo")
                return
            
            # Save student photo
            photo_save_path = self.database.save_student_photo(student_id, image)
            if not photo_save_path:
                messagebox.showerror("Error", "Failed to save student photo")
                return
            
            # Generate QR code
            qr_save_path = self.database.generate_qr_code(student_id)
            if not qr_save_path:
                messagebox.showerror("Error", "Failed to generate QR code")
                return
            
            # Create student object
            student = Student(
                student_id=student_id,
                name=student_name,
                faculty=faculty,
                graduation_level=graduation_level,
                photo_path=photo_save_path,
                qr_code_path=qr_save_path,
                face_encoding=face_encoding.tolist(),
                attendance="Pending"
            )
            
            # Save to database
            if self.database.add_student(student):
                # Success - clean up temporary file if it exists
                if temp_file_to_cleanup:
                    self.cleanup_temp_file(temp_file_to_cleanup)
                
                messagebox.showinfo("Success", 
                                  f"Student {student_name} (ID: {student_id}) registered successfully!")
                self.clear_form()
                
                # Update parent window status if available
                try:
                    self.frame.master.master.update_status_bar()
                except:
                    pass
            else:
                messagebox.showerror("Error", "Failed to save student data")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error registering student: {str(e)}")
        finally:
            # Clean up temporary file even if registration failed
            if temp_file_to_cleanup:
                self.cleanup_temp_file(temp_file_to_cleanup)
    
    def clear_form(self):
        """Clear all form fields"""
        # Clean up temporary file if exists
        if self.photo_path and self.photo_path.startswith('temp_'):
            self.cleanup_temp_file(self.photo_path)
        
        self.student_id_var.set("")
        self.student_name_var.set("")
        self.faculty_var.set("")
        self.graduation_level_var.set("")
        self.photo_path = None
        self.photo_label.config(text="No photo selected")
        self.photo_preview.configure(image="")
        self.photo_preview.image = None
    
    def refresh_data(self):
        """Refresh data (called after database restore)"""
        self.clear_form()


class PhotoCaptureWindow:
    """Photo capture window"""
    
    def __init__(self, parent, face_engine):
        self.face_engine = face_engine
        self.captured_photo_path = None
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("📷 Take Student Photo")
        self.window.geometry("700x630")
        self.window.configure(bg='lightgray')
        
        # Make modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Handle window close event to clean up camera
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        self.setup_ui()
        self.start_camera()
    
    def setup_ui(self):
        """Setup capture window UI"""
        # Instructions
        instruction_frame = ttk.Frame(self.window)
        instruction_frame.pack(fill='x', padx=10, pady=5)
        
        instruction_text = "📋 Position face in the green rectangle, then click 'CAPTURE PHOTO'"
        ttk.Label(instruction_frame, text=instruction_text, 
                 foreground="darkblue", font=('Arial', 10, 'bold')).pack()
        
        # Camera display
        self.camera_label = ttk.Label(self.window, background='black')
        self.camera_label.pack(padx=10, pady=10)
        
        # Status label
        self.status_label = ttk.Label(self.window, text="📸 Ready to capture", 
                                      foreground="green", font=('Arial', 12, 'bold'))
        self.status_label.pack(pady=5)
        
        # Button frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="📸 CAPTURE PHOTO", 
                  command=self.capture_photo).pack(side='left', padx=10)
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=self.cancel).pack(side='left', padx=10)
        
        self.current_frame = None
        self.cap = None
    
    def start_camera(self):
        """Start camera capture"""
        self.cap = cv2.VideoCapture(Config.CAMERA_INDEX)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Cannot open camera")
            self.window.destroy()
            return
        
        self.update_camera()
    
    def update_camera(self):
        """Update camera display"""
        if not self.cap:
            return
        
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            faces = self.face_engine.get_face_bounding_boxes(frame_rgb)
            
            if faces:
                self.status_label.config(text="✅ Face detected - Ready!", foreground="green")
                for bbox in faces:
                    cv2.rectangle(frame_rgb, (bbox[0], bbox[1]), 
                                (bbox[2], bbox[3]), (0, 255, 0), 3)
            else:
                self.status_label.config(text="⚠️ Position face in frame", foreground="orange")
            
            # Convert to PIL and display
            pil_image = Image.fromarray(frame_rgb)
            pil_image = pil_image.resize(Config.CAMERA_DISPLAY_SIZE)
            photo = ImageTk.PhotoImage(pil_image)
            
            self.camera_label.configure(image=photo)
            self.camera_label.image = photo
            
            self.current_frame = frame_rgb
        
        if self.window.winfo_exists():
            self.window.after(30, self.update_camera)
    
    def capture_photo(self):
        """Capture current frame"""
        if self.current_frame is None:
            messagebox.showwarning("Warning", "No frame available")
            return
        
        # Verify face exists
        faces = self.face_engine.get_face_bounding_boxes(self.current_frame)
        if not faces:
            messagebox.showwarning("Warning", "No face detected. Please position face properly.")
            return
        
        # Save photo with temp prefix for cleanup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_path = f"temp_capture_{timestamp}.jpg"
        
        frame_bgr = cv2.cvtColor(self.current_frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(temp_path, frame_bgr)
        
        self.captured_photo_path = temp_path
        
        self.cleanup_camera()
        self.window.destroy()
        messagebox.showinfo("Success", "Photo captured successfully!")
    
    def cancel(self):
        """Cancel capture"""
        self.cleanup_camera()
        self.window.destroy()
    
    def on_window_close(self):
        """Handle window close event"""
        self.cleanup_camera()
        self.window.destroy()
    
    def cleanup_camera(self):
        """Clean up camera resources"""
        if self.cap:
            self.cap.release()
            self.cap = None