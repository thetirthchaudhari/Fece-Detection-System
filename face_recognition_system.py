import cv2
import numpy as np
import torch
from mtcnn import MTCNN
from facenet_pytorch import MTCNN as FacenetMTCNN, InceptionResnetV1
import pickle
import os
from database import StudentDatabase
from datetime import datetime

class FaceRecognitionSystem:
    def __init__(self):
        # Initialize MTCNN for face detection
        self.mtcnn = MTCNN()
        
        # Initialize FaceNet model for face recognition
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        
        # Initialize database
        self.db = StudentDatabase()
        
        # Load known faces
        self.known_faces = {}
        self.known_encodings = []
        self.known_names = []
        self.known_enrollments = []
        self.load_known_faces()
        
        # Track recent attendance to prevent duplicates
        self.recent_attendance = {}
    
    def load_known_faces(self):
        """Load known faces from database"""
        students = self.db.get_all_students()
        for student in students:
            student_id, name, enrollment, face_encoding = student
            if face_encoding:
                # Convert blob back to numpy array
                encoding = np.frombuffer(face_encoding, dtype=np.float32)
                self.known_encodings.append(encoding)
                self.known_names.append(name)
                self.known_enrollments.append(enrollment)
                self.known_faces[enrollment] = {
                    'name': name,
                    'encoding': encoding,
                    'id': student_id
                }
    
    def capture_face(self, enrollment_number, name):
        """Capture and enroll a new student's face with multiple angles"""
        cap = cv2.VideoCapture(0)
        print(f"Capturing face for {name} ({enrollment_number})")
        print("Instructions:")
        print("1. Look straight at camera - Press SPACE")
        print("2. Turn head slightly left - Press SPACE")
        print("3. Turn head slightly right - Press SPACE")
        print("4. Press ENTER when done, ESC to cancel")
        
        captured_encodings = []
        capture_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Detect faces
            faces = self.mtcnn.detect_faces(frame)
            
            # Draw rectangle around detected face
            if faces:
                for face in faces:
                    x, y, w, h = face['box']
                    confidence = face['confidence']
                    
                    if confidence > 0.8:  # Lowered confidence threshold
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(frame, f"Confidence: {confidence:.2f}", 
                                  (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                        
                        # Extract face region
                        face_img = frame[y:y+h, x:x+w]
                        
                        # Generate face encoding
                        face_tensor = self.preprocess_face(face_img)
                        if face_tensor is not None:
                            with torch.no_grad():
                                face_encoding = self.resnet(face_tensor).cpu().numpy()
                            
                            captured_encodings.append(face_encoding.flatten())
            
            cv2.putText(frame, f"Captures: {capture_count}/3", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, "Press SPACE to capture, ENTER when done, ESC to cancel", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.imshow('Face Capture - Multiple Angles', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):  # Space to capture
                if faces and faces[0]['confidence'] > 0.8 and len(captured_encodings) > capture_count:
                    capture_count += 1
                    print(f"Capture {capture_count}/3 completed")
            elif key == 13:  # Enter to finish
                if capture_count >= 1:  # At least one capture
                    break
            elif key == 27:  # ESC to cancel
                cap.release()
                cv2.destroyAllWindows()
                return False
        
        # Average the captured encodings for better recognition
        if captured_encodings:
            avg_encoding = np.mean(captured_encodings, axis=0)
            
            # Save to database
            encoding_blob = avg_encoding.tobytes()
            success = self.db.add_student(name, enrollment_number, encoding_blob)
            
            if success:
                print(f"Successfully enrolled {name} with {capture_count} captures")
                # Update known faces
                self.known_encodings.append(avg_encoding)
                self.known_names.append(name)
                self.known_enrollments.append(enrollment_number)
                self.known_faces[enrollment_number] = {
                    'name': name,
                    'encoding': avg_encoding,
                    'id': len(self.known_faces) + 1
                }
                cap.release()
                cv2.destroyAllWindows()
                return True
        
        cap.release()
        cv2.destroyAllWindows()
        return False
    
    def preprocess_face(self, face_img):
        """Preprocess face image for FaceNet model"""
        try:
            # Resize to 160x160 (FaceNet input size)
            face_img = cv2.resize(face_img, (160, 160))
            # Convert BGR to RGB
            face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            # Normalize pixel values
            face_img = (face_img - 127.5) / 128.0
            # Convert to tensor
            face_tensor = torch.FloatTensor(face_img).permute(2, 0, 1).unsqueeze(0)
            return face_tensor.to(self.device)
        except Exception as e:
            print(f"Error preprocessing face: {e}")
            return None
    
    def recognize_face(self, face_encoding, threshold=1.2):
        """Recognize a face from encoding with improved tolerance"""
        if len(self.known_encodings) == 0:
            return "Unknown", "Unknown", None
        
        # Calculate distances to all known faces
        distances = []
        for known_encoding in self.known_encodings:
            # Calculate cosine similarity for better angle tolerance
            face_norm = face_encoding.flatten() / np.linalg.norm(face_encoding.flatten())
            known_norm = known_encoding / np.linalg.norm(known_encoding)
            cosine_sim = np.dot(face_norm, known_norm)
            distance = 1 - cosine_sim  # Convert similarity to distance
            distances.append(distance)
        
        # Find the best match
        min_distance = min(distances)
        best_match_idx = distances.index(min_distance)
        
        if min_distance < threshold:
            return (self.known_names[best_match_idx], 
                   self.known_enrollments[best_match_idx], 
                   self.known_faces[self.known_enrollments[best_match_idx]]['id'])
        else:
            return "Unknown", "Unknown", None
    
    def detect_and_recognize(self):
        """Main function for real-time face detection and recognition"""
        cap = cv2.VideoCapture(0)
        print("Starting face recognition system...")
        print("Press 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Detect faces using MTCNN
            faces = self.mtcnn.detect_faces(frame)
            
            # Display current time at the top of the screen
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, f"System Time: {current_time}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            for face in faces:
                x, y, w, h = face['box']
                confidence = face['confidence']
                
                if confidence > 0.8:  # Lowered confidence threshold for better detection
                    # Extract face region
                    face_img = frame[y:y+h, x:x+w]
                    
                    # Generate face encoding
                    face_tensor = self.preprocess_face(face_img)
                    if face_tensor is not None:
                        with torch.no_grad():
                            face_encoding = self.resnet(face_tensor).cpu().numpy()
                        
                        # Recognize face
                        name, enrollment, student_id = self.recognize_face(face_encoding)
                        
                        # Calculate confidence score for display
                        if name != "Unknown":
                            # Get the confidence score
                            face_norm = face_encoding.flatten() / np.linalg.norm(face_encoding.flatten())
                            known_encoding = self.known_faces[enrollment]['encoding']
                            known_norm = known_encoding / np.linalg.norm(known_encoding)
                            confidence_score = np.dot(face_norm, known_norm)
                            confidence_percent = int(confidence_score * 100)
                        else:
                            confidence_percent = 0
                        
                        # Draw rectangle and label
                        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                        
                        label = f"{name} ({enrollment})" if name != "Unknown" else "Unknown"
                        cv2.putText(frame, label, (x, y-10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                        
                        # Display confidence score
                        if name != "Unknown":
                            cv2.putText(frame, f"Confidence: {confidence_percent}%", (x, y+h+10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                        
                        # Mark attendance if recognized (prevent duplicates within 30 seconds)
                        if name != "Unknown" and student_id:
                            current_time = datetime.now()
                            student_key = f"{enrollment}_{name}"
                            
                            # Check if attendance was already marked recently
                            if student_key not in self.recent_attendance or \
                               (current_time - self.recent_attendance[student_key]).seconds > 30:
                                
                                self.db.mark_attendance(student_id, name, enrollment)
                                self.recent_attendance[student_key] = current_time
                                
                                time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
                                cv2.putText(frame, "Attendance Marked!", (x, y+h+20), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                                cv2.putText(frame, f"Time: {time_str}", (x, y+h+40), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                            else:
                                cv2.putText(frame, "Already Marked", (x, y+h+20), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            
            cv2.imshow('Face Recognition Attendance System', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()


