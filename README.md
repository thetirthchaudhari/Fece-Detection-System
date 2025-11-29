# Face Recognition Attendance System

A comprehensive face recognition-based attendance system using MTCNN for face detection and FaceNet for face recognition.

## Features

1. **Face Capture**: Capture and enroll new students' faces
2. **Face Detection**: Real-time face detection using MTCNN
3. **Face Recognition**: Recognize students using FaceNet model
4. **Database Integration**: Store student information and attendance records
5. **Excel Export**: Export attendance with name, enrollment number, and timestamp
6. **Unknown Face Handling**: Display "Unknown" for unrecognized faces

## Requirements

- Python 3.7+
- OpenCV
- MTCNN
- FaceNet (facenet-pytorch)
- TensorFlow
- PyTorch
- SQLite3
- Pandas
- OpenPyXL
- Tkinter

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have a webcam connected to your system.

## Usage

1. Run the main application:
```bash
python main.py
```

2. **Adding Students**:
   - Click "Add New Student"
   - Enter student name and enrollment number
   - Position face in front of camera
   - Press SPACE to capture, ESC to cancel

3. **Taking Attendance**:
   - Click "Start Recognition"
   - Students' faces will be detected and recognized automatically
   - Attendance is marked automatically for recognized students
   - Unknown faces will be labeled as "Unknown"
   - Press 'q' to stop recognition

4. **Exporting Reports**:
   - Export all attendance records to Excel
   - Export daily attendance for specific dates
   - View attendance summary

## System Components

### 1. Face Recognition System (`face_recognition_system.py`)
- Uses MTCNN for accurate face detection
- Implements FaceNet model for face recognition
- Handles face enrollment and recognition
- Manages real-time attendance marking

### 2. Database Management (`database.py`)
- SQLite database for student information
- Stores face encodings and attendance records
- Handles student enrollment and attendance tracking

### 3. Excel Export (`excel_export.py`)
- Exports attendance records to Excel format
- Includes student name, enrollment number, and timestamp
- Supports daily and complete attendance exports

### 4. Main Application (`main.py`)
- GUI interface using Tkinter
- Integrates all system components
- Provides easy-to-use interface for all operations

## Database Schema

### Students Table
- `id`: Primary key
- `name`: Student name
- `enrollment_number`: Unique enrollment number
- `face_encoding`: Face encoding data (BLOB)
- `created_at`: Timestamp

### Attendance Table
- `id`: Primary key
- `student_id`: Foreign key to students table
- `name`: Student name
- `enrollment_number`: Student enrollment number
- `timestamp`: Attendance timestamp

## Technical Details

- **Face Detection**: MTCNN (Multi-task CNN) for robust face detection
- **Face Recognition**: FaceNet model trained on VGGFace2 dataset
- **Face Encoding**: 512-dimensional face embeddings
- **Recognition Threshold**: Cosine similarity threshold of 0.6
- **Confidence Threshold**: 0.9 for face detection

## Troubleshooting

1. **Camera Issues**: Ensure webcam is connected and accessible
2. **Model Loading**: First run may take time to download pre-trained models
3. **Recognition Accuracy**: Ensure good lighting and clear face visibility
4. **Database Errors**: Check file permissions for database creation

## Future Enhancements

- Batch student enrollment from images
- Attendance analytics and reports
- Integration with existing student management systems
- Mobile app support
- Cloud deployment options

## License

This project is open source and available under the MIT License.

