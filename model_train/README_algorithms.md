# Face Recognition Algorithm Comparison

This project contains separate implementations for three different face recognition algorithms, each with its own virtual environment to avoid dependency conflicts.

## Project Structure

```
model_train/
├── insightface_algorithm/
│   ├── insightface_test.py    # InsightFace implementation
│   ├── requirements.txt       # InsightFace dependencies
│   ├── setup.bat             # Setup script
│   ├── run.bat               # Run script
│   └── venv/                 # Virtual environment (created after setup)
├── facenet_algorithm/
│   ├── facenet_test.py       # FaceNet implementation
│   ├── requirements.txt      # FaceNet dependencies
│   ├── setup.bat             # Setup script
│   ├── run.bat               # Run script
│   └── venv/                 # Virtual environment (created after setup)
├── vggface_algorithm/
│   ├── vggface_test.py       # VGGFace implementation
│   ├── requirements.txt      # VGGFace dependencies
│   ├── setup.bat             # Setup script
│   ├── run.bat               # Run script
│   └── venv/                 # Virtual environment (created after setup)
├── dlib_algorithm/
│   ├── dlib_test.py          # Dlib implementation
│   ├── requirements.txt      # Dlib dependencies
│   ├── setup.bat             # Setup script
│   ├── run.bat               # Run script
│   ├── models/               # Downloaded dlib models (created automatically)
│   └── venv/                 # Virtual environment (created after setup)
└── archive/                  # LFW dataset (shared)
```

## Algorithm Descriptions

### 1. InsightFace
- **Technology**: ONNX-based face recognition
- **Advantages**: Fast, accurate, no TensorFlow dependency
- **Dependencies**: NumPy < 2.0, ONNX 1.16.1, OpenCV
- **Status**: ✅ Working (tested)

### 2. FaceNet
- **Technology**: TensorFlow/Keras with InceptionV3 backbone
- **Advantages**: Well-established architecture, good accuracy
- **Dependencies**: TensorFlow 2.x, MTCNN for face detection
- **Status**: ⚠️ Requires TensorFlow 2.x setup

### 3. VGGFace
- **Technology**: VGG16-based feature extraction
- **Advantages**: Simple, interpretable features
- **Dependencies**: TensorFlow 2.x, MTCNN for face detection
- **Status**: ⚠️ Requires TensorFlow 2.x setup

### 4. Dlib
- **Technology**: ResNet-based face recognition with 68-point landmarks
- **Advantages**: No deep learning framework dependency, good accuracy, robust
- **Dependencies**: Dlib, OpenCV, CMake for compilation
- **Status**: 🔄 Ready to setup (requires model download)

## Setup Instructions

### Option 1: Automatic Setup (Recommended)

1. **For InsightFace**:
   ```cmd
   cd insightface_algorithm
   setup.bat
   ```

2. **For FaceNet**:
   ```cmd
   cd facenet_algorithm
   setup.bat
   ```

3. **For VGGFace**:
   ```cmd
   cd vggface_algorithm
   setup.bat
   ```

4. **For Dlib**:
   ```cmd
   cd dlib_algorithm
   setup.bat
   ```

### Option 2: Manual Setup

1. Navigate to the desired algorithm folder
2. Create virtual environment:
   ```cmd
   python -m venv venv
   ```
3. Activate virtual environment:
   ```cmd
   venv\Scripts\activate.bat
   ```
4. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

## Running the Tests

### Option 1: Using Run Scripts (Recommended)

1. **For InsightFace**:
   ```cmd
   cd insightface_algorithm
   run.bat
   ```

2. **For FaceNet**:
   ```cmd
   cd facenet_algorithm
   run.bat
   ```

3. **For VGGFace**:
   ```cmd
   cd vggface_algorithm
   run.bat
   ```

4. **For Dlib**:
   ```cmd
   cd dlib_algorithm
   run.bat
   ```

### Option 2: Manual Execution

1. Navigate to the algorithm folder
2. Activate virtual environment:
   ```cmd
   venv\Scripts\activate.bat
   ```
3. Run the test:
   ```cmd
   python <algorithm>_test.py
   ```

## Results

Each algorithm will:
- Process 100 LFW face pairs by default
- Calculate accuracy, F1 score, precision, and recall
- Generate a visualization chart
- Save results in the `result/` folder within each algorithm directory

## Troubleshooting

### Common Issues:

1. **NumPy compatibility errors**:
   - InsightFace: Uses NumPy < 2.0 (resolved)
   - FaceNet/VGGFace: May need NumPy version adjustments

2. **TensorFlow import errors**:
   - Ensure you're using the correct virtual environment
   - Try downgrading/upgrading TensorFlow version if needed

3. **CUDA warnings**:
   - Normal for CPU-only execution
   - Can be ignored unless you want GPU acceleration

### Environment Isolation Benefits:

- **No dependency conflicts** between algorithms
- **Independent package versions** for each algorithm
- **Easy to test** different configurations
- **Clean uninstall** by simply deleting the venv folder

## Performance Comparison

After running all algorithms, you can compare:
- **Accuracy**: How often the algorithm correctly identifies same/different persons
- **F1 Score**: Harmonic mean of precision and recall
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **Processing Speed**: Time to process the test dataset
- **Skipped Pairs**: Number of pairs that couldn't be processed (indicates robustness)

## Dataset

The algorithms use the LFW (Labeled Faces in the Wild) dataset located in the `archive/` folder. The dataset contains:
- Face images organized by person
- Pair files for verification tasks
- Same person pairs and different person pairs for evaluation

## Next Steps

1. **Start with InsightFace** (known working)
2. **Setup TensorFlow environments** for FaceNet and VGGFace
3. **Compare results** across all algorithms
4. **Optimize thresholds** for better accuracy
5. **Scale up testing** with more pairs (change from 100 to 1000+ pairs)
