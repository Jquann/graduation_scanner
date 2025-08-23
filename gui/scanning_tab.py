#!/usr/bin/env python3
"""
Real-time face recognition and QR scanning tab
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import queue
import time
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


class ScanningTab:
    """Real-time recognition interface"""
    
    def __init__(self, parent, camera_worker, qr_manager, database, config):
        self.camera_worker = camera_worker
        self.qr_manager = qr_manager
        self.database = database
        self.config = config
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Initialize variables
        self.qr_input_var = tk.StringVar()
        self.is_scanning = False
        
        # Setup UI
        self.setup_ui()
        
        # Start GUI update loop
        self.update_gui_loop()
    
    def setup_ui(self):
        """Setup scanning interface"""
        # Control buttons
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        self.start_button = ttk.Button(
            control_frame, 
            text="🚀 Start Student Recognition", 
            command=self.start_scanning
        )
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(
            control_frame, 
            text="⏹️ Stop Recognition", 
            command=self.stop_scanning, 
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=5)
        
        # Status indicators
        self.status_label = ttk.Label(control_frame, text="Status: Ready", foreground="blue")
        self.status_label.pack(side='left', padx=20)
        
        self.perf_label = ttk.Label(control_frame, text="FPS: 0", foreground="green")
        self.perf_label.pack(side='right', padx=20)
        
        self.qr_status_label = ttk.Label(control_frame, text="QR: None", foreground="gray")
        self.qr_status_label.pack(side='right', padx=10)
        
        # Main content area
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left side: Camera display
        self.setup_camera_area(main_frame)
        
        # Right side: QR input area
        self.setup_qr_area(main_frame)
        
        # Bottom: Results display
        self.setup_results_area()
    
    def setup_camera_area(self, parent):
        """Setup camera display area"""
        camera_frame = ttk.LabelFrame(parent, text="👤 Face Recognition Camera")
        camera_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.camera_label = ttk.Label(
            camera_frame, 
            text="Camera will appear here when started\n\n" +
                 "Position face in view for recognition"
        )
        self.camera_label.pack(padx=10, pady=10)
    
    def setup_qr_area(self, parent):
        """Setup QR code input area"""
        qr_frame = ttk.LabelFrame(parent, text="📱 QR Code Management")
        qr_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Instructions
        instruction_frame = ttk.Frame(qr_frame)
        instruction_frame.pack(fill='x', padx=10, pady=5)
        
        instruction_text = f"""📋 Instructions:
1. Start face recognition first
2. Input QR code using methods below
3. QR persists for {self.config['qr_timeout']}s
4. System tries {self.config['max_match_attempts']} times
5. Manual override available if needed"""
        
        ttk.Label(
            instruction_frame, 
            text=instruction_text, 
            justify='left', 
            foreground="darkblue"
        ).pack(anchor='w')
        
        # Input methods
        input_method_frame = ttk.LabelFrame(qr_frame, text="Input Method")
        input_method_frame.pack(fill='x', padx=10, pady=10)
        
        # Manual input
        self.setup_manual_input(input_method_frame)
        
        # Image import
        self.setup_image_import(input_method_frame)
        
        # QR status display
        self.setup_qr_status(qr_frame)
    
    def setup_manual_input(self, parent):
        """Setup manual QR input"""
        manual_frame = ttk.Frame(parent)
        manual_frame.pack(fill='x', pady=5)
        
        ttk.Label(
            manual_frame, 
            text="Method 1 - Manual Input:", 
            font=('Arial', 9, 'bold')
        ).pack(anchor='w')
        
        entry_frame = ttk.Frame(manual_frame)
        entry_frame.pack(fill='x', pady=5)
        
        ttk.Label(entry_frame, text="Student ID:").pack(side='left')
        
        self.qr_entry = ttk.Entry(entry_frame, textvariable=self.qr_input_var, width=20)
        self.qr_entry.pack(side='left', padx=5)
        
        ttk.Button(
            entry_frame, 
            text="✅ Submit", 
            command=self.submit_manual_qr
        ).pack(side='left', padx=5)
        
        # Bind Enter key
        self.qr_entry.bind('<Return>', lambda e: self.submit_manual_qr())
    
    def setup_image_import(self, parent):
        """Setup QR image import"""
        image_frame = ttk.Frame(parent)
        image_frame.pack(fill='x', pady=10)
        
        ttk.Label(
            image_frame, 
            text="Method 2 - Import QR Image:", 
            font=('Arial', 9, 'bold')
        ).pack(anchor='w')
        
        button_frame = ttk.Frame(image_frame)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            button_frame, 
            text="📁 Import QR Image", 
            command=self.import_qr_image
        ).pack(side='left', padx=5)
        
        self.qr_image_label = ttk.Label(image_frame, text="No QR image selected")
        self.qr_image_label.pack(anchor='w', pady=5)
    
    def setup_qr_status(self, parent):
        """Setup QR status display"""
        self.current_qr_frame = ttk.LabelFrame(parent, text="Current QR Status")
        self.current_qr_frame.pack(fill='x', padx=10, pady=10)
        
        self.current_qr_label = ttk.Label(
            self.current_qr_frame, 
            text="No QR data loaded", 
            foreground="gray"
        )
        self.current_qr_label.pack(pady=5)
        
        # Timing and attempt info
        self.qr_timing_label = ttk.Label(
            self.current_qr_frame, 
            text="", 
            foreground="blue", 
            font=('Arial', 8)
        )
        self.qr_timing_label.pack(pady=2)
        
        self.qr_attempts_label = ttk.Label(
            self.current_qr_frame, 
            text="", 
            foreground="orange", 
            font=('Arial', 8)
        )
        self.qr_attempts_label.pack(pady=2)
        
        # Control buttons
        qr_control_frame = ttk.Frame(self.current_qr_frame)
        qr_control_frame.pack(pady=5)
        
        ttk.Button(
            qr_control_frame, 
            text="🗑️ Clear QR", 
            command=self.clear_qr_data
        ).pack(side='left', padx=2)
        
        ttk.Button(
            qr_control_frame, 
            text="🔄 Reset Attempts", 
            command=self.reset_qr_attempts
        ).pack(side='left', padx=2)
        
        ttk.Button(
            qr_control_frame, 
            text="⏭️ Force Success", 
            command=self.force_qr_success
        ).pack(side='left', padx=2)
    
    def setup_results_area(self):
        """Setup recognition results display"""
        result_frame = ttk.LabelFrame(self.frame, text="🎓 Student Recognition Results")
        result_frame.pack(fill='x', padx=5, pady=(5, 0))
        
        # Create scrollable text area
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.result_text = tk.Text(text_frame, height=8, wrap=tk.WORD)
        self.result_text.pack(side='left', fill='both', expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.result_text.configure(yscrollcommand=scrollbar.set)
    
    def start_scanning(self):
        """Start real-time recognition"""
        if self.is_scanning:
            return
        
        if self.database.get_student_count() == 0:
            messagebox.showwarning("Warning", "No students registered. Please register students first.")
            return
        
        self.is_scanning = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="Status: 🔴 ACTIVE", foreground="red")
        
        # Clear result display
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "🚀 Face Recognition System Started\n")
        self.result_text.insert(tk.END, "=" * 50 + "\n")
        self.result_text.insert(tk.END, f"📺 Display FPS: {self.config['display_fps']}\n")
        self.result_text.insert(tk.END, f"🔍 Detection FPS: {self.config['detection_fps']}\n")
        self.result_text.insert(tk.END, f"⏰ QR Timeout: {self.config['qr_timeout']} seconds\n")
        self.result_text.insert(tk.END, f"🔄 Max Attempts: {self.config['max_match_attempts']}\n")
        self.result_text.insert(tk.END, "=" * 50 + "\n\n")
        
        # Start camera worker
        self.camera_worker.start()
    
    def stop_scanning(self):
        """Stop real-time recognition"""
        self.is_scanning = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="Status: ⚪ STOPPED", foreground="gray")
        self.perf_label.config(text="FPS: 0")
        self.qr_status_label.config(text="QR: None", foreground="gray")
        
        # Stop camera worker
        self.camera_worker.stop()
        
        self.result_text.insert(tk.END, "\n" + "=" * 50 + "\n")
        self.result_text.insert(tk.END, "⏹️ Face Recognition System Stopped\n")
        self.result_text.see(tk.END)
    
    def submit_manual_qr(self):
        """Submit manually entered QR code"""
        qr_data = self.qr_input_var.get().strip()
        if not qr_data:
            messagebox.showwarning("Warning", "Please enter a Student ID")
            return
        
        self.qr_manager.set_current_qr(qr_data, "Manual Input")
        self.qr_input_var.set("")
        
        if self.is_scanning:
            self.add_result_message(
                f"📱 NEW QR CODE LOADED\n" +
                f"🆔 Student ID: {qr_data}\n" +
                f"📥 Source: Manual Input\n" +
                f"⏰ Timeout: {self.config['qr_timeout']} seconds\n" +
                f"🔍 Starting face recognition...\n"
            )
    
    def import_qr_image(self):
        """Import and decode QR code from image"""
        file_path = filedialog.askopenfilename(
            title="Select QR Code Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if not file_path:
            return
        
        qr_data = self.qr_manager.decode_qr_from_image(file_path)
        
        if qr_data:
            self.qr_manager.set_current_qr(qr_data, f"Image: {os.path.basename(file_path)}")
            self.qr_image_label.config(text=f"✅ Loaded: {os.path.basename(file_path)}")
            messagebox.showinfo("Success", f"QR code decoded: {qr_data}")
            
            if self.is_scanning:
                self.add_result_message(
                    f"📱 QR CODE FROM IMAGE\n" +
                    f"🆔 Student ID: {qr_data}\n" +
                    f"📥 Source: {os.path.basename(file_path)}\n"
                )
        else:
            messagebox.showerror("Error", "No QR code found in image")
    
    def clear_qr_data(self):
        """Clear current QR data"""
        self.qr_manager.clear_current_qr()
        self.current_qr_label.config(text="No QR data loaded", foreground="gray")
        self.qr_image_label.config(text="No QR image selected")
        self.qr_timing_label.config(text="")
        self.qr_attempts_label.config(text="")
        self.qr_input_var.set("")
        
        if self.is_scanning:
            self.add_result_message("🗑️ QR data cleared\n")
    
    def reset_qr_attempts(self):
        """Reset QR matching attempts"""
        self.qr_manager.reset_attempts()
        
        if self.is_scanning:
            qr_data = self.qr_manager.get_current_qr()
            if qr_data:
                self.add_result_message(
                    f"🔄 ATTEMPTS RESET for QR: {qr_data.data}\n" +
                    f"📊 Attempt counter reset to 0\n"
                )
    
    def force_qr_success(self):
        """Force mark current QR as successful"""
        qr_data = self.qr_manager.get_current_qr()
        if not qr_data:
            messagebox.showwarning("Warning", "No QR data loaded")
            return
        
        from face_matching import FaceMatcher
        matcher = FaceMatcher(None, self.qr_manager, self.config)
        result = matcher.force_match(qr_data.data)
        
        if result:
            self.display_match_result(result.to_display_dict())
            self.qr_manager.clear_current_qr()
            messagebox.showinfo("Manual Override", f"Manually confirmed: {result.name}")
        else:
            messagebox.showerror("Error", f"Student ID {qr_data.data} not found")
    
    def update_qr_status_display(self):
        """Update QR status display"""
        qr_status = self.qr_manager.get_qr_status_info()
        
        if qr_status['has_qr']:
            # Update QR label
            self.current_qr_label.config(
                text=f"📱 QR: {qr_status['data']}", 
                foreground="blue"
            )
            
            # Update timing
            remaining = qr_status['remaining_time']
            minutes = int(remaining) // 60
            seconds = int(remaining) % 60
            
            self.qr_timing_label.config(
                text=f"⏱️ Time remaining: {minutes}:{seconds:02d}",
                foreground="blue" if remaining > 10 else "orange"
            )
            
            # Update attempts
            attempts = qr_status['attempt_count']
            max_attempts = qr_status['max_attempts']
            
            self.qr_attempts_label.config(
                text=f"🔄 Attempts: {attempts}/{max_attempts}",
                foreground="green" if attempts < max_attempts * 0.7 else "red"
            )
            
            # Update main status
            self.qr_status_label.config(
                text=f"QR: {qr_status['data']} ({int(remaining)}s)",
                foreground="blue" if remaining > 10 else "red"
            )
        else:
            self.current_qr_label.config(text="No QR data loaded", foreground="gray")
            self.qr_timing_label.config(text="")
            self.qr_attempts_label.config(text="")
            self.qr_status_label.config(text="QR: None", foreground="gray")
    
    def process_results(self):
        """Process results from camera worker"""
        try:
            while True:
                message_type, data = self.camera_worker.result_queue.get_nowait()
                
                if message_type == "camera_frame":
                    # Update camera display
                    self.camera_label.configure(image=data)
                    self.camera_label.image = data
                    
                    # Update FPS
                    stats = self.camera_worker.get_performance_stats()
                    self.perf_label.config(text=f"FPS: {stats['fps']}")
                
                elif message_type == "match_found":
                    self.display_match_result(data)
                
                elif message_type == "similarity_low":
                    self.display_low_similarity(data)
                
                elif message_type == "student_not_found":
                    self.display_student_not_found(data)
                
                elif message_type == "qr_timeout":
                    self.display_qr_timeout(data)
                
                elif message_type == "error":
                    self.add_result_message(f"❌ Error: {data}\n")
                    
        except queue.Empty:
            pass
    
    def display_match_result(self, data):
        """Display successful match"""
        result_text = f"""
🎉 RECOGNITION SUCCESSFUL 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ Time: {data['timestamp']}
🆔 Student ID: {data['student_id']}
👤 Name: {data['name']}
🏛️ Faculty: {data['faculty']}
🎓 Level: {data['graduation_level']}
📊 Similarity: {data['similarity']:.3f}
🎯 Confidence: {data['confidence_level']}/5
🔄 Attempts: {data.get('total_attempts', 0)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        self.add_result_message(result_text)
    
    def display_low_similarity(self, data):
        """Display low similarity warning"""
        result_text = f"""
⚠️ ATTEMPTING ({data['attempt']}/{data['max_attempts']})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ Time: {data['timestamp']}
🆔 ID: {data['student_id']}
👤 Expected: {data['student_name']}
📊 Similarity: {data['similarity']:.3f}
📊 Required: {data['required']:.3f}
💡 {data['suggestion']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        self.add_result_message(result_text)
    
    def display_student_not_found(self, data):
        """Display student not found message"""
        result_text = f"""
❌ STUDENT NOT FOUND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ Time: {data['timestamp']}
🆔 Student ID: {data['student_id']}
❌ Not registered in system
💡 Please check ID or register first
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        self.add_result_message(result_text)
    
    def display_qr_timeout(self, data):
        """Display QR timeout message"""
        result_text = f"""
⏰ QR CODE TIMEOUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆔 Student ID: {data['data']}
⏰ Timeout after: {self.config['qr_timeout']}s
🔄 Total attempts: {data['attempt_count']}
💡 Please scan QR code again
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        self.add_result_message(result_text)
    
    def add_result_message(self, message):
        """Add message to result display"""
        self.result_text.insert(tk.END, message)
        self.result_text.see(tk.END)
    
    def update_gui_loop(self):
        """Main GUI update loop"""
        if self.is_scanning:
            # Update QR status
            self.update_qr_status_display()
            
            # Process results
            self.process_results()
        
        # Schedule next update
        self.frame.after(self.config.get('gui_update_ms', 33), self.update_gui_loop)