# Graduation Scanner - Modular Architecture

An intelligent face recognition system for graduation ceremonies with anti-spoofing capabilities, now refactored into a clean, maintainable modular architecture.

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
│   └── management_tab.py     # Student management interface
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

#### `gui/management_tab.py`
- Student database management
- Search, filter, and sorting functionality
- Data export/import (CSV, JSON, Excel)
- Attendance report generation with charts

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

## 🔧 Configuration

### Performance Profiles

| Mode | Detection FPS | Display FPS | Buffer Size | Anti-Spoofing |
|------|--------------|-------------|-------------|---------------|
| low_cpu | 1 | 25 | Small | Enabled |
| balanced | 2 | 30 | Medium | Enabled |
| high_performance | 5 | 30 | Large | Enabled |

### Customization

Edit `config.py` to customize:
- Detection parameters and thresholds
- GUI settings and window sizes
- File paths and directory structure
- Performance parameters
- Anti-spoofing sensitivity

## 🔄 Migration from Monolithic Version

To migrate from the original single-file version:

1. Backup your existing `graduation_data` folder
2. Install the modular version in a new directory
3. Copy your `graduation_data` folder to the new location
4. Install additional dependencies (TensorFlow for anti-spoofing)
5. Run the application - it will automatically use existing data

## 🐛 Troubleshooting

### Common Issues

1. **Face detection slow**: Switch to `low_cpu` mode or reduce detection frequency
2. **Import errors**: Ensure all dependencies are installed, especially TensorFlow
3. **QR decode errors**: Install system zbar library (see Prerequisites)
4. **TensorFlow not found**: Install TensorFlow using: `pip install tensorflow>=2.13.0`
5. **Anti-spoofing disabled**: Ensure TensorFlow is properly installed and models can be loaded
6. **TTS not working**: Check pyttsx3 installation and system audio configuration
7. **Export/Import errors**: Ensure openpyxl is installed for Excel functionality
8. **Student ID validation**: Use format 11AAA11111 (2 digits + 3 letters + 5 digits)
9. **Attendance not updating**: Ensure database permissions are correct and storage is available

### Performance Issues

- For older systems: Use `low_cpu` mode and reduce camera resolution
- For memory issues: Reduce buffer sizes in configuration
- For slow recognition: Check face image quality and lighting conditions

## 📝 License

This project is provided as-is for educational and commercial use.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review module documentation in code comments
3. Ensure all system dependencies are properly installed
4. Check TensorFlow installation for anti-spoofing issues
5. Verify camera permissions and availability

## 📋 System Requirements

### Minimum Requirements
- Python 3.8+
- 4GB RAM
- 2GB free disk space
- USB/Built-in camera
- Audio output device (for TTS)

### Recommended Requirements
- Python 3.9+
- 8GB RAM
- 4GB free disk space
- HD camera (720p or better)
- Good lighting conditions for face recognition

---

**Version**: 1.1.0  
**Last Updated**: 2025  
**Features**: Face Recognition, Anti-Spoofing, QR Validation, TTS Announcements, Data Management, Enhanced Visual Feedback