#!/usr/bin/env python3
"""
Certificate display functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os

class CertificateDisplay:
    """Certificate display window for ceremonies"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.is_fullscreen = False
        self.current_student = None
        self.certificate_canvas = None
        
        # Certificate styling
        self.colors = {
            'bg': '#1a1a2e',  # Dark navy background
            'primary': '#16213e',  # Darker blue
            'accent': '#0f3460',  # Medium blue
            'gold': '#ffd700',  # Gold accent
            'text_primary': '#ffffff',
            'text_secondary': '#b8c5d1',
            'border': '#2c5282'
        }
        
        self.create_display_window()
    
    def create_display_window(self):
        """Create the certificate display window"""
        if self.window:
            self.window.lift()
            return
            
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Certificate Display - Ceremony Mode")
        self.window.geometry("1200x800")
        self.window.configure(bg=self.colors['bg'])
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.setup_certificate_ui()
    
    def setup_certificate_ui(self):
        """Setup the certificate display interface"""
        # Control panel at top (hidden in fullscreen)
        self.control_frame = tk.Frame(self.window, bg=self.colors['primary'], height=50)
        self.control_frame.pack(fill='x', side='top')
        self.control_frame.pack_propagate(False)
        
        # Control buttons
        btn_frame = tk.Frame(self.control_frame, bg=self.colors['primary'])
        btn_frame.pack(expand=True)
        
        tk.Button(btn_frame, text="Toggle Fullscreen", 
                 command=self.toggle_fullscreen,
                 bg=self.colors['accent'], fg='white',
                 font=('Arial', 10, 'bold'),
                 relief='flat', padx=20).pack(side='left', padx=10, pady=10)
        
        tk.Button(btn_frame, text="Clear Display", 
                 command=self.clear_certificate,
                 bg=self.colors['accent'], fg='white',
                 font=('Arial', 10, 'bold'),
                 relief='flat', padx=20).pack(side='left', padx=5, pady=10)
        
        tk.Button(btn_frame, text="Test Display", 
                 command=self.show_test_certificate,
                 bg=self.colors['gold'], fg='black',
                 font=('Arial', 10, 'bold'),
                 relief='flat', padx=20).pack(side='left', padx=5, pady=10)
        
        # Status label
        self.status_label = tk.Label(self.control_frame, 
                                   text="Certificate Display Ready - Scan QR Code to Begin",
                                   bg=self.colors['primary'], fg=self.colors['text_secondary'],
                                   font=('Arial', 12))
        self.status_label.pack(side='right', padx=20)
        
        # Main certificate area
        self.cert_frame = tk.Frame(self.window, bg=self.colors['bg'])
        self.cert_frame.pack(fill='both', expand=True)
        
        # Create certificate canvas
        self.certificate_canvas = tk.Canvas(self.cert_frame, 
                                          bg=self.colors['bg'],
                                          highlightthickness=0)
        self.certificate_canvas.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Bind resize event
        self.certificate_canvas.bind('<Configure>', self.on_canvas_resize)
        
        self.show_welcome_screen()
    
    def show_welcome_screen(self):
        """Show welcome screen when no certificate is displayed"""
        self.certificate_canvas.delete("all")
        
        # Get canvas dimensions
        self.window.update_idletasks()
        width = self.certificate_canvas.winfo_width()
        height = self.certificate_canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            width, height = 800, 600
        
        center_x, center_y = width // 2, height // 2
        
        # Background gradient effect (simulated with rectangles)
        for i in range(0, width, 20):
            alpha = abs(i - width//2) / (width//2)
            color_val = int(26 + alpha * 20)  # Gradient from dark to slightly lighter
            color = f"#{color_val:02x}{color_val:02x}{max(46, color_val + 20):02x}"
            self.certificate_canvas.create_rectangle(i, 0, i+20, height, 
                                                   fill=color, outline=color)
        
        # Welcome content
        self.certificate_canvas.create_text(center_x, center_y - 100,
                                          text="🎓 CEREMONY CERTIFICATE DISPLAY 🎓",
                                          fill=self.colors['gold'],
                                          font=('Arial', 28, 'bold'),
                                          anchor='center')
        
        self.certificate_canvas.create_text(center_x, center_y - 40,
                                          text="Ready to Display Graduate Information",
                                          fill=self.colors['text_primary'],
                                          font=('Arial', 18),
                                          anchor='center')
        
        self.certificate_canvas.create_text(center_x, center_y + 20,
                                          text="• Scan QR Code for automatic display",
                                          fill=self.colors['text_secondary'],
                                          font=('Arial', 14),
                                          anchor='center')
        
        self.certificate_canvas.create_text(center_x, center_y + 50,
                                          text="• Press F11 or use button to toggle fullscreen",
                                          fill=self.colors['text_secondary'],
                                          font=('Arial', 14),
                                          anchor='center')
        
        self.certificate_canvas.create_text(center_x, center_y + 80,
                                          text="• Perfect for graduation ceremonies",
                                          fill=self.colors['text_secondary'],
                                          font=('Arial', 14),
                                          anchor='center')
        
        # Decorative border
        self.certificate_canvas.create_rectangle(50, 50, width-50, height-50,
                                               outline=self.colors['border'],
                                               width=3, fill='')
    
    def display_certificate(self, student_data):
        """Display certificate for a student"""
        self.current_student = student_data
        self.certificate_canvas.delete("all")
        
        # Get canvas dimensions
        self.window.update_idletasks()
        width = self.certificate_canvas.winfo_width()
        height = self.certificate_canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            width, height = 800, 600
        
        # Create elegant certificate design
        self.draw_certificate_background(width, height)
        self.draw_certificate_content(width, height, student_data)
        
        # Update status
        self.status_label.config(text=f"Displaying: {student_data.get('name', 'N/A')}")
    
    def draw_certificate_background(self, width, height):
        """Draw certificate background with elegant design"""
        # Main background with gradient effect
        for i in range(height):
            ratio = i / height
            # Gradient from dark navy to slightly lighter
            r = int(26 + ratio * 15)
            g = int(26 + ratio * 20) 
            b = int(46 + ratio * 30)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.certificate_canvas.create_line(0, i, width, i, fill=color)
        
        # Decorative border with multiple layers
        border_margin = 40
        
        # Outer gold border
        self.certificate_canvas.create_rectangle(border_margin, border_margin,
                                               width - border_margin, height - border_margin,
                                               outline=self.colors['gold'], width=4, fill='')
        
        # Inner border
        inner_margin = border_margin + 20
        self.certificate_canvas.create_rectangle(inner_margin, inner_margin,
                                               width - inner_margin, height - inner_margin,
                                               outline=self.colors['text_secondary'], width=2, fill='')
        
        # Corner decorations
        corner_size = 60
        corners = [
            (border_margin, border_margin),  # Top-left
            (width - border_margin - corner_size, border_margin),  # Top-right
            (border_margin, height - border_margin - corner_size),  # Bottom-left
            (width - border_margin - corner_size, height - border_margin - corner_size)  # Bottom-right
        ]
        
        for x, y in corners:
            self.draw_corner_decoration(x, y, corner_size)
    
    def draw_corner_decoration(self, x, y, size):
        """Draw decorative corner elements"""
        # Golden corner accent
        points = [x + size//2, y, x + size, y + size//2, x + size//2, y + size, x, y + size//2]
        self.certificate_canvas.create_polygon(points, fill=self.colors['gold'], outline='')
        
        # Inner diamond
        inner_size = size // 3
        inner_x, inner_y = x + size//2, y + size//2
        inner_points = [
            inner_x, inner_y - inner_size//2,
            inner_x + inner_size//2, inner_y,
            inner_x, inner_y + inner_size//2,
            inner_x - inner_size//2, inner_y
        ]
        self.certificate_canvas.create_polygon(inner_points, fill=self.colors['bg'], outline='')
    
    def draw_certificate_content(self, width, height, student_data):
        """Draw certificate content with student information"""
        center_x = width // 2
        
        # Title
        self.certificate_canvas.create_text(center_x, height * 0.15,
                                          text="GRADUATION CERTIFICATE",
                                          fill=self.colors['gold'],
                                          font=('Times New Roman', 42, 'bold'),
                                          anchor='center')
        
        # Subtitle
        self.certificate_canvas.create_text(center_x, height * 0.22,
                                          text="This certifies that",
                                          fill=self.colors['text_secondary'],
                                          font=('Times New Roman', 20, 'italic'),
                                          anchor='center')
        
        # Student Name (highlighted)
        name = student_data.get('name', 'N/A')
        self.certificate_canvas.create_text(center_x, height * 0.35,
                                          text=name.upper(),
                                          fill=self.colors['text_primary'],
                                          font=('Times New Roman', 48, 'bold'),
                                          anchor='center')
        
        # Create a temporary text item to measure actual width
        temp_text = self.certificate_canvas.create_text(0, 0, text=name.upper(),
                                                       font=('Times New Roman', 48, 'bold'))
        bbox = self.certificate_canvas.bbox(temp_text)
        self.certificate_canvas.delete(temp_text)
        
        if bbox:
            text_width = bbox[2] - bbox[0]
        else:
            text_width = len(name) * 28

        self.certificate_canvas.create_line(center_x - text_width//2, height * 0.40,
                                          center_x + text_width//2, height * 0.40,
                                          fill=self.colors['gold'], width=3)
        
        # Student ID
        student_id = student_data.get('student_id', 'N/A')
        self.certificate_canvas.create_text(center_x, height * 0.43,
                                          text=f"Student ID: {student_id}",
                                          fill=self.colors['text_secondary'],
                                          font=('Arial', 18),
                                          anchor='center')
        
        # Achievement text
        self.certificate_canvas.create_text(center_x, height * 0.52,
                                          text="has successfully completed the requirements for",
                                          fill=self.colors['text_secondary'],
                                          font=('Times New Roman', 20, 'italic'),
                                          anchor='center')
        
        # Graduation Level
        graduation_level = student_data.get('graduation_level', 'N/A')
        self.certificate_canvas.create_text(center_x, height * 0.60,
                                          text=graduation_level,
                                          fill=self.colors['gold'],
                                          font=('Times New Roman', 36, 'bold'),
                                          anchor='center')
        
        # Faculty/Department
        faculty = student_data.get('faculty', 'N/A')
        self.certificate_canvas.create_text(center_x, height * 0.68,
                                          text=f"Faculty of {faculty}",
                                          fill=self.colors['text_primary'],
                                          font=('Times New Roman', 24),
                                          anchor='center')
        
        # Date
        current_date = datetime.now().strftime("%B %d, %Y")
        self.certificate_canvas.create_text(center_x, height * 0.80,
                                          text=f"Awarded on {current_date}",
                                          fill=self.colors['text_secondary'],
                                          font=('Times New Roman', 18),
                                          anchor='center')
        
        # Congratulations message
        self.certificate_canvas.create_text(center_x, height * 0.88,
                                          text="🎉 CONGRATULATIONS! 🎉",
                                          fill=self.colors['gold'],
                                          font=('Arial', 24, 'bold'),
                                          anchor='center')
    
    def show_test_certificate(self):
        """Show a test certificate for demonstration"""
        test_data = {
            'name': 'John Smith Doe',
            'student_id': '22CSC12345',
            'faculty': 'Computer Science and Information Technology',
            'graduation_level': 'Bachelor of Computer Science (Honours)'
        }
        self.display_certificate(test_data)
    
    def clear_certificate(self):
        """Clear the certificate display"""
        self.current_student = None
        self.show_welcome_screen()
        self.status_label.config(text="Certificate Display Ready - Scan QR Code to Begin")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        self.window.attributes('-fullscreen', self.is_fullscreen)
        
        if self.is_fullscreen:
            self.control_frame.pack_forget()
            # Bind Escape key to exit fullscreen
            self.window.bind('<Escape>', lambda e: self.toggle_fullscreen())
            self.window.bind('<F11>', lambda e: self.toggle_fullscreen())
        else:
            self.control_frame.pack(fill='x', side='top')
            self.window.unbind('<Escape>')
            self.window.unbind('<F11>')
        
        # Refresh display
        if self.current_student:
            self.display_certificate(self.current_student)
        else:
            self.show_welcome_screen()
    
    def on_canvas_resize(self, event):
        """Handle canvas resize event"""
        if self.current_student:
            self.display_certificate(self.current_student)
        else:
            self.show_welcome_screen()
    
    def on_close(self):
        """Handle window close"""
        if self.window:
            self.window.destroy()
            self.window = None
    
    def is_open(self):
        """Check if certificate window is open"""
        return self.window is not None and self.window.winfo_exists()


# Integration class for adding to main application
class CertificateIntegration:
    """Integration helper for adding certificate display to existing application"""
    
    def __init__(self):
        self.certificate_display = None
    
    def add_certificate_button(self, parent_frame):
        """Add certificate display button to parent frame"""
        cert_button = ttk.Button(parent_frame, text="🎓 Certificate Display", 
                               command=self.open_certificate_display)
        return cert_button
    
    def open_certificate_display(self):
        """Open certificate display window"""
        if self.certificate_display is None or not self.certificate_display.is_open():
            self.certificate_display = CertificateDisplay()
        else:
            self.certificate_display.window.lift()
    
    def show_student_certificate(self, student_data):
        """Show certificate for a student (called after successful QR + face detection)"""
        if self.certificate_display is None or not self.certificate_display.is_open():
            self.certificate_display = CertificateDisplay()
        
        # Convert student object to dict if necessary
        if hasattr(student_data, '__dict__'):
            data = {
                'name': student_data.name,
                'student_id': student_data.student_id,
                'faculty': student_data.faculty,
                'graduation_level': student_data.graduation_level
            }
        else:
            data = student_data
        
        self.certificate_display.display_certificate(data)
        self.certificate_display.window.lift()


# Example usage and integration instructions
if __name__ == "__main__":
    # Standalone test
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    # Create certificate display
    cert_display = CertificateDisplay(root)
    
    root.mainloop