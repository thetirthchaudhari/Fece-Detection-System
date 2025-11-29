import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import sys

def test_imports():
    """Test if all required packages are installed"""
    try:
        import cv2
        print("✓ OpenCV imported successfully")
        
        import mtcnn
        print("✓ MTCNN imported successfully")
        
        import tensorflow as tf
        print("✓ TensorFlow imported successfully")
        
        import torch
        print("✓ PyTorch imported successfully")
        
        import facenet_pytorch
        print("✓ FaceNet imported successfully")
        
        import pandas as pd
        print("✓ Pandas imported successfully")
        
        print("\n🎉 All packages are installed correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def simple_face_capture():
    """Simple face capture test"""
    try:
        import cv2
        
        print("\n📸 Testing webcam...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Webcam not found or not accessible")
            return False
        
        print("✓ Webcam is working!")
        print("Press 'q' to quit, SPACE to capture")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            
            cv2.putText(frame, "Press SPACE to capture, 'q' to quit", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow('Webcam Test', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):
                print("✓ Face capture test successful!")
                cv2.imwrite('test_face.jpg', frame)
                print("✓ Test image saved as 'test_face.jpg'")
                break
            elif key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        return True
        
    except Exception as e:
        print(f"❌ Webcam test failed: {e}")
        return False

def main():
    print("🧪 Face Recognition System Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Some packages are missing. Please install them first.")
        return
    
    # Test webcam
    if not simple_face_capture():
        print("\n❌ Webcam test failed.")
        return
    
    print("\n✅ All tests passed!")
    print("\n🚀 You can now run the main application:")
    print("   python main.py")

if __name__ == "__main__":
    main()






