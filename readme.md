# Graduation Scanner - Modular Architecture

An intelligent face recognition system for graduation ceremonies, now refactored into a clean, maintainable modular architecture.

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

1. Python 3.8 or higher
2. System dependencies for pyzbar:
   - **Ubuntu/Debian**: `sudo apt-get install libzbar0`
   - **macOS**: `brew install zbar`
   - **Windows**: Download from [zbar website](http://zbar.sourceforge.net/download.html)

### Setup

1. Clone or download the project
2. Navigate to the project directory
3. Install Python dependencies:

```bash
pip install -r requirements.txt
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

### Debug Mode

Enable verbose output for troubleshooting:

```bash
python main.py --debug
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
- Student data persistence
- CRUD operations
- Backup and restore functionality
- Photo and QR code management

#### `face_recognition.py`
- InsightFace model wrapper
- Face detection and encoding extraction
- Similarity calculation algorithms
- Dynamic threshold adjustment

#### `qr_manager.py`
- QR code generation and decoding
- QR data persistence with timeout
- Attempt tracking and history
- QR status management

#### `camera_worker.py`
- Multi-threaded camera capture
- Asynchronous face detection
- Performance optimization
- Queue-based communication

#### `face_matching.py`
- Face matching logic
- Buffer management
- Consecutive match confirmation
- Result processing

### GUI Modules

#### `gui/main_window.py`
- Main application window
- Menu bar and status bar
- Tab container management
- Application lifecycle

#### `gui/registration_tab.py`
- Student registration form
- Photo capture/selection
- Input validation
- Registration workflow

#### `gui/scanning_tab.py`
- Real-time recognition interface
- QR input methods (manual, image)
- Recognition results display
- Status indicators

#### `gui/management_tab.py`
- Student list view
- CRUD operations
- Student details viewer
- Database statistics

## 🎯 Features

### QR Persistence
- QR data persists for configurable timeout (30-60 seconds)
- Multiple face matching attempts
- Dynamic similarity threshold adjustment
- Manual override options

### Performance Optimization
- Dual-frequency processing (display vs detection)
- Asynchronous face detection
- Configurable buffer sizes
- CPU usage optimization

### User-Friendly Interface
- Tabbed interface for different functions
- Real-time status indicators
- Visual feedback for face detection
- Comprehensive result display

## 🔧 Configuration

### Performance Profiles

| Mode | Detection FPS | Display FPS | QR Timeout | Max Attempts |
|------|--------------|-------------|------------|--------------|
| low_cpu | 1 | 25 | 30s | 15 |
| balanced | 2 | 30 | 45s | 25 |
| high_performance | 5 | 30 | 60s | 40 |

### Customization

Edit `config.py` to customize:
- Detection parameters
- GUI settings
- File paths
- Threshold values

## 📊 Benefits of Modular Architecture

1. **Separation of Concerns**: Each module has a single, clear responsibility
2. **Easier Testing**: Components can be tested independently
3. **Better Collaboration**: Multiple developers can work on different modules
4. **Reusability**: Modules can be reused in other projects
5. **Maintainability**: Bugs are easier to locate and fix
6. **Scalability**: New features can be added without affecting existing code
7. **Cleaner Code**: Improved readability and organization

## 🔄 Migration from Monolithic Version

To migrate from the original single-file version:

1. Backup your existing `graduation_data` folder
2. Install the modular version in a new directory
3. Copy your `graduation_data` folder to the new location
4. Run the application - it will automatically use existing data

## 🐛 Troubleshooting

### Common Issues

1. **Camera not detected**: Check camera index in Camera Settings
2. **Face detection slow**: Switch to `low_cpu` mode
3. **Import errors**: Ensure all dependencies are installed
4. **QR decode errors**: Install system zbar library

### Debug Mode

Run with `--debug` flag for detailed error messages:

```bash
python main.py --debug
```

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

To extend the functionality:

1. Add new modules in appropriate directories
2. Follow the existing naming conventions
3. Update imports in `__init__.py` files
4. Document new features in README

## 📞 Support

For issues or questions:
1. Check the User Guide in Help menu
2. Run in debug mode for detailed errors
3. Review module documentation in code comments

---

**Version**: 1.0.0  
**Last Updated**: 2025