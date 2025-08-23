#!/usr/bin/env python3
"""
Main GUI window for Graduation Scanner
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from face_recognition import FaceRecognitionEngine
from qr_manager import QRCodeManager
from camera_worker import CameraWorker
from database import StudentDatabase

from gui.registration_tab import RegistrationTab
from gui.scanning_tab import ScanningTab
from gui.management_tab import ManagementTab


class GraduationScannerApp:
    """Main application window"""
    
    def __init__(self, performance_mode='balanced'):
        # Initialize configuration
        self.config = Config.get_performance_config(performance_mode)
        self.performance_mode = performance_mode
        
        # Create necessary directories
        Config.create_directories()
        
        # Initialize components
        self.face_engine = FaceRecognitionEngine(performance_mode)
        self.qr_manager = QRCodeManager(self.config)
        self.camera_worker = CameraWorker(self.face_engine, self.qr_manager, self.config)
        self.database = StudentDatabase()
        
        # Initialize GUI
        self.setup_gui()
        
        # Set window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_gui(self):
        """Setup main GUI window"""
        self.root = tk.Tk()
        self.root.title(Config.APP_NAME)
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        
        # Set window icon if available
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.create_status_bar()
        
        # Create notebook widget (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(10, 0))
        
        # Create tabs
        self.registration_tab = RegistrationTab(
            self.notebook, 
            self.face_engine, 
            self.database
        )
        
        self.scanning_tab = ScanningTab(
            self.notebook,
            self.camera_worker,
            self.qr_manager,
            self.database,
            self.config
        )
        
        self.management_tab = ManagementTab(
            self.notebook,
            self.database
        )
        
        # Add tabs to notebook
        self.notebook.add(self.registration_tab.frame, text="Student Registration")
        self.notebook.add(self.scanning_tab.frame, text="Student Recognition")
        self.notebook.add(self.management_tab.frame, text="Student Management")
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Backup Database", command=self.backup_database)
        file_menu.add_command(label="Restore Database", command=self.restore_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Performance Settings", command=self.show_performance_settings)
        tools_menu.add_command(label="Camera Settings", command=self.show_camera_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_status_bar(self):
        """Create status bar at bottom of window"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side='bottom', fill='x')
        
        # Performance mode indicator
        self.mode_label = ttk.Label(
            self.status_bar,
            text=f"Mode: {self.performance_mode.title()}",
            relief=tk.SUNKEN,
            anchor='w'
        )
        self.mode_label.pack(side='left', padx=5)
        
        # Student count
        self.student_count_label = ttk.Label(
            self.status_bar,
            text=f"Students: {self.database.get_student_count()}",
            relief=tk.SUNKEN,
            anchor='w'
        )
        self.student_count_label.pack(side='left', padx=5)
        
        # Version info
        self.version_label = ttk.Label(
            self.status_bar,
            text=f"v{Config.APP_VERSION}",
            relief=tk.SUNKEN,
            anchor='e'
        )
        self.version_label.pack(side='right', padx=5)
    
    def update_status_bar(self):
        """Update status bar information"""
        self.student_count_label.config(text=f"Students: {self.database.get_student_count()}")
    
    def backup_database(self):
        """Backup database to file"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.database.backup_database(file_path):
                messagebox.showinfo("Success", "Database backed up successfully!")
            else:
                messagebox.showerror("Error", "Failed to backup database")
    
    def restore_database(self):
        """Restore database from file"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            if messagebox.askyesno("Confirm", "This will replace all current data. Continue?"):
                if self.database.restore_database(file_path):
                    self.registration_tab.refresh_data()
                    self.management_tab.refresh_student_list()
                    self.update_status_bar()
                    messagebox.showinfo("Success", "Database restored successfully!")
                else:
                    messagebox.showerror("Error", "Failed to restore database")
    
    def show_performance_settings(self):
        """Show performance settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Performance Settings")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Performance Mode:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        mode_var = tk.StringVar(value=self.performance_mode)
        
        for mode in ['low_cpu', 'balanced', 'high_performance']:
            ttk.Radiobutton(
                dialog,
                text=mode.replace('_', ' ').title(),
                variable=mode_var,
                value=mode
            ).pack(pady=5)
        
        def apply_settings():
            new_mode = mode_var.get()
            if new_mode != self.performance_mode:
                messagebox.showinfo("Info", "Please restart the application for changes to take effect")
            dialog.destroy()
        
        ttk.Button(dialog, text="Apply", command=apply_settings).pack(pady=20)
    
    def show_camera_settings(self):
        """Show camera settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Camera Settings")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Camera Index:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        camera_var = tk.IntVar(value=Config.CAMERA_INDEX)
        ttk.Spinbox(dialog, from_=0, to=5, textvariable=camera_var, width=10).pack(pady=10)
        
        ttk.Label(dialog, text="Note: Changes require restart", foreground="blue").pack(pady=10)
        
        ttk.Button(dialog, text="OK", command=dialog.destroy).pack(pady=10)
    
    def show_user_guide(self):
        """Show user guide"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("User Guide")
        guide_window.geometry("600x400")
        
        text_widget = tk.Text(guide_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill='both', expand=True)
        
        guide_text = """
GRADUATION SCANNER USER GUIDE

1. STUDENT REGISTRATION
   - Enter student details (ID, Name, Faculty, Graduation Level)
   - Choose or capture a photo
   - Click "Register Student" to save

2. FACE RECOGNITION
   - Start the recognition system
   - Input QR code (manual or image)
   - System will match faces automatically
   - Results appear in real-time

3. STUDENT MANAGEMENT
   - View all registered students
   - Delete or edit student records
   - View detailed information

TIPS:
- Ensure good lighting for face recognition
- Keep face centered in camera view
- QR codes persist for configured timeout
- Use manual override if needed
        """
        
        text_widget.insert('1.0', guide_text)
        text_widget.config(state='disabled')
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""
{Config.APP_NAME}
Version {Config.APP_VERSION}

An intelligent face recognition system
for graduation ceremonies.

Using InsightFace for face recognition
and QR codes for student identification.

© 2025 - All rights reserved
        """
        messagebox.showinfo("About", about_text)
    
    def on_closing(self):
        """Handle window closing"""
        if self.camera_worker.is_running:
            if messagebox.askyesno("Confirm", "Recognition is running. Stop and exit?"):
                self.camera_worker.stop()
            else:
                return
        
        self.root.destroy()
    
    def run(self):
        """Run the application"""
        print(f"Starting {Config.APP_NAME}...")
        print(f"Performance Mode: {self.performance_mode}")
        self.root.mainloop()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Graduation Scanner Application')
    parser.add_argument(
        '--mode',
        choices=['low_cpu', 'balanced', 'high_performance'],
        default='balanced',
        help='Performance mode'
    )
    
    args = parser.parse_args()
    
    try:
        app = GraduationScannerApp(performance_mode=args.mode)
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()