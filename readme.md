# Graduation Scanner - Modular Architecture

An intelligent face recognition system for graduation ceremonies with anti-spoofing capabilities and certificate display functionality, built with a clean, maintainable modular architecture.

## 🏗️ Project Structure

```
graduation_scanner/
│
├── main.py                    # Application entry point
├── config.py                  # Configuration management
├── models.py                  # Data models and structures
├── database.py                # Student data persistence
├── face_recognition.py        # Face recognition engine
├── qr_manager.py             # QR code management
├── camera_worker.py          # Camera and threading
├── face_matching.py          # Face matching logic
│
├── gui/                      # GUI components
│   ├── __init__.py
│   ├── main_window.py        # Main application window
│   ├── registration_tab.py   # Student registration interface
│   ├── scanning_tab.py       # Real-time recognition interface
│   ├── management_tab.py     # Student management interface
│   └── certificate_display.py # Certificate ceremony display
│
├── DeepFaceModel/            # Anti-spoofing models
│   ├── __init__.py
│   ├── FasNet.py            # Fasnet anti-spoofing implementation
│   ├── FasNetBackbone.py    # Fasnet model architecture
│   ├── folder_utils.py      # Folder management utilities
│   ├── logger.py            # Logging utilities
│   ├── package_utils.py     # Package validation utilities
│   └── weight_utils.py      # Model weight management
│
├── graduation_data/          # Data directory (auto-created)
│   ├── photos/              # Student photos
│   ├── qrcodes/             # Generated QR codes
│   └── students_data.json   # Student database
│
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🚀 Installation

### Prerequisites

1. **Python 3.8 or higher**
2. **System dependencies for pyzbar:**
   - **Ubuntu/Debian**: `sudo apt-get install libzbar0`
   - **macOS**: `brew install zbar`
   - **Windows**: Download and install from [zbar website](http://zbar.sourceforge.net/download.html)
3. **TensorFlow** (for anti-spoofing functionality)
   - **CPU version**: `pip install tensorflow>=2.13.0 tf-keras>=2.13.0`
   - **GPU version**: Visit [TensorFlow website](https://www.tensorflow.org/install) for GPU-specific installation
4. **System audio** (for text-to-speech functionality)
   - Most systems have this by default
   - Linux users may need: `sudo apt-get install espeak espeak-data`
5. **GUI framework dependencies:**
   - **Ubuntu/Debian**: `sudo apt-get install python3-tk`
   - **Most other systems**: tkinter included by default

### Setup

1. Clone or download the project
2. Navigate to the project directory
3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. **For TensorFlow** (required for anti-spoofing):
```bash
# CPU version (recommended for most users)
pip install tensorflow>=2.13.0 tf-keras>=2.13.0

# Or GPU version if you have CUDA-compatible GPU
# Follow TensorFlow GPU installation guide
```

## 💻 Usage

### Basic Usage

Run the application with default settings:

```bash
python main.py
```

### Performance Modes

Choose a performance mode based on your system:

```bash
# Low CPU usage mode (for older systems)
python main.py --mode low_cpu

# Balanced mode (default)
python main.py --mode balanced

# High performance mode (for powerful systems)
python main.py --mode high_performance
```

## 📁 Module Descriptions

### Core Modules

#### `config.py`
- Centralized configuration management
- Performance profiles (low_cpu, balanced, high_performance)
- Application settings and constants

#### `models.py`
- Data models using dataclasses
- Student, QRData, RecognitionResult models
- Performance statistics tracking

#### `database.py`
- Student data persistence with JSON format
- CRUD operations for student records
- Photo and QR code file management
- Data validation and backup functionality

#### `face_recognition.py`
- InsightFace model wrapper for face detection and recognition
- Face encoding extraction using buffalo_l model
- Similarity calculation algorithms
- Integration with anti-spoofing detection

#### `qr_manager.py`
- QR code generation and decoding
- Student ID validation through QR codes
- QR data persistence and timeout management
- Image-based QR code detection

#### `camera_worker.py`
- Multi-threaded camera capture
- Real-time face detection processing
- Performance-optimized frame handling
- Queue-based communication with GUI

#### `face_matching.py`
- Face matching logic with configurable thresholds
- Buffer management for consecutive matches
- Integration with QR validation system
- Result processing and logging

### Anti-Spoofing Module (`DeepFaceModel/`)

#### `FasNet.py`
- Main anti-spoofing engine using MiniFASNet models
- Real-time spoofing detection
- TensorFlow-based model inference

#### `FasNetBackbone.py`
- Neural network architectures for spoofing detection
- MiniFASNetV1SE and MiniFASNetV2 implementations
- Squeeze-and-Excitation modules

#### Utility Modules
- `logger.py`: Centralized logging system
- `folder_utils.py`: Directory management
- `package_utils.py`: Dependency validation
- `weight_utils.py`: Model weight download and management

### GUI Modules

#### `gui/main_window.py`
- Main application window with tabbed interface
- Menu bar and status bar
- Application lifecycle management
- Performance mode display

#### `gui/registration_tab.py`
- Student registration form with validation
- Photo capture/selection functionality
- Student ID format validation (11AAA11111)
- Face detection verification

#### `gui/scanning_tab.py`
- Real-time recognition interface with enhanced visual feedback
- QR input methods (manual entry, image upload)
- Live camera feed with face detection overlays
- Comprehensive recognition status indicators
- Automatic attendance marking on successful recognition
- Visual feedback for recognition attempts, success, and failures
- Progress tracking for matching attempts
- Integration with certificate display system

#### `gui/management_tab.py`
- Student database management
- Search, filter, and sorting functionality
- Data export/import (CSV, JSON, Excel)
- Attendance report generation with charts

#### `gui/certificate_display.py`
- **NEW**: Elegant certificate display window for graduation ceremonies
- Fullscreen presentation mode for projectors/large displays
- Real-time certificate generation with student information
- Integration with face recognition system for automatic display
- Professional graduation certificate design with gold accents
- Manual controls for ceremony management
- Test mode for setup verification

## 🎯 Features

### Enhanced Student Management
- Comprehensive student registration with photo capture
- Student ID validation (format: 11AAA11111)
- Faculty and graduation level tracking
- Attendance status management

### Face Recognition System
- InsightFace buffalo_l model for accurate recognition
- Real-time face detection and matching
- Configurable similarity thresholds
- Performance optimization for different system capabilities

### Anti-Spoofing Protection
- TensorFlow-based MiniFASNet models
- Real-time spoofing detection during recognition
- Configurable spoofing sensitivity
- Live face validation

### QR Code Integration
- Automatic QR code generation for each student
- QR-based student lookup and validation
- Support for manual QR entry and image upload
- QR code timeout and attempt tracking

### Enhanced Visual Feedback System
- Real-time recognition status indicators
- Live accuracy percentage display
- Student information overlay
- Progress tracking for matching attempts
- Color-coded status messages (green for success, orange for attempts, red for errors)
- Interactive feedback with contextual tips and instructions
- Automatic attendance marking on successful recognition

### **NEW: Certificate Display System**
- **Professional Certificate Presentation**: Elegant, ceremony-ready certificate display
- **Real-time Integration**: Automatic certificate display upon successful face recognition
- **Fullscreen Ceremony Mode**: Perfect for projectors and large displays during graduations
- **Dynamic Content**: Displays student name, ID, faculty, and graduation level
- **Professional Design**: Gold-accented certificates with decorative borders
- **Manual Controls**: Test mode, clear display, and ceremony management controls
- **Responsive Design**: Adapts to different screen sizes and resolutions
- **Instant Display**: Certificate appears immediately after successful QR + face recognition

### Data Management
- JSON-based database with backup functionality
- Export to multiple formats (CSV, JSON, Excel)
- Import from CSV and JSON files

### Reporting and Analytics
- PDF attendance reports with charts
- Faculty-wise attendance statistics
- Visual analytics with matplotlib integration
- Print-ready QR codes

### Text-to-Speech Announcements
- Automated name announcements during recognition
- Faculty and graduation level reading
- Configurable voice settings

## 🎓 Ceremony Usage Workflow

### Setup Phase
1. Launch the application and register all students
2. Generate QR codes for all students
3. Open Certificate Display from the scanning tab
4. Set display to fullscreen mode for ceremony presentation
5. Test the system with sample QR codes

### During Ceremony
1. Start face recognition system
2. Student approaches with QR code
3. Scan QR code (manual entry or image upload)
4. Student looks at camera for face recognition
5. Upon successful match:
   - Attendance is automatically marked as "Present"
   - Certificate is instantly displayed on screen
   - Student name and details appear elegantly
   - TTS announcement (if enabled)

### Certificate Display Features
- **Automatic Display**: No manual intervention needed during ceremony
- **Professional Appearance**: Gold-accented design suitable for formal ceremonies
- **Student Information**: Name, Student ID, Faculty, and Graduation Level
- **Real-time Generation**: Each certificate is created instantly with current date
- **Fullscreen Mode**: Perfect for projector displays during ceremonies
- **Manual Override**: Force display certificates if needed for special cases

## 🔧 Configuration

### Performance Profiles

| Mode | Detection FPS | Display FPS | Buffer Size | Anti-Spoofing | Certificate Display |
|------|--------------|-------------|-------------|---------------|-------------------|
| low_cpu | 1 | 25 | Small | Enabled | Enabled |
| balanced | 2 | 30 | Medium | Enabled | Enabled |
| high_performance | 5 | 30 | Large | Enabled | Enabled |

### Customization

Edit `config.py` to customize:
- Detection parameters and thresholds
- GUI settings and window sizes
- File paths and directory structure
- Performance parameters
- Anti-spoofing sensitivity
- Certificate display styling
- QR timeout and retry settings

## 🔄 Migration from Previous Versions

To migrate from older versions:

1. Backup your existing `graduation_data` folder
2. Install the new version in a fresh directory
3. Copy your `graduation_data` folder to the new location
4. Install new dependencies (especially Pillow for certificate generation)
5. Run the application - existing data will be preserved
6. Access new certificate display through the scanning tab

## 🐛 Troubleshooting

### Common Issues

1. **Face detection slow**: Switch to `low_cpu` mode or reduce detection frequency
2. **Import errors**: Ensure all dependencies are installed, especially TensorFlow and Pillow
3. **QR decode errors**: Install system zbar library (see Prerequisites)
4. **TensorFlow not found**: Install TensorFlow using: `pip install tensorflow>=2.13.0`
5. **Anti-spoofing disabled**: Ensure TensorFlow is properly installed and models can be loaded
6. **TTS not working**: Check pyttsx3 installation and system audio configuration
7. **Export/Import errors**: Ensure openpyxl is installed for Excel functionality
8. **Student ID validation**: Use format 11AAA11111 (2 digits + 3 letters + 5 digits)
9. **Attendance not updating**: Ensure database permissions are correct and storage is available
10. **Certificate display not showing**: Ensure Pillow is installed and display window has focus
11. **Certificate styling issues**: Check font availability and canvas size settings

### Performance Issues

- For older systems: Use `low_cpu` mode and reduce camera resolution
- For memory issues: Reduce buffer sizes in configuration
- For slow recognition: Check face image quality and lighting conditions
- For certificate display lag: Ensure adequate RAM and close unnecessary applications

### Certificate Display Issues

1. **Certificate not appearing**: Check if certificate window is minimized or behind other windows
2. **Blurry text**: Ensure adequate screen resolution and proper fullscreen mode
3. **Layout issues**: Test different screen resolutions and aspect ratios
4. **Font problems**: System fonts are used; ensure standard fonts are available

## 📝 License

This project is provided as-is for educational and commercial use.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review module documentation in code comments
3. Ensure all system dependencies are properly installed
4. Check TensorFlow installation for anti-spoofing issues
5. Verify camera permissions and availability
6. Test certificate display in windowed mode before fullscreen

## 📋 System Requirements

### Minimum Requirements
- Python 3.8+
- 4GB RAM
- 2GB free disk space
- USB/Built-in camera
- Audio output device (for TTS)
- Display capable of 1024x768 resolution

### Recommended Requirements for Ceremonies
- Python 3.9+
- 8GB RAM
- 4GB free disk space
- HD camera (720p or better)
- Projector or large display (1920x1080 recommended)
- Good lighting conditions for face recognition
- Stable internet connection (for initial model downloads)

### Ceremony Setup Requirements
- Projector or large screen for certificate display
- Adequate lighting for face recognition
- QR code reader or camera for QR scanning
- Audio system for TTS announcements (optional)
- Backup power supply recommended

---

**Version**: 1.0.0  
**Last Updated**: 2025  
**New Features**: Certificate Display System, Enhanced Visual Feedback, Ceremony Mode  
**Core Features**: Face Recognition, Anti-Spoofing, QR Validation, TTS Announcements, Data Management
