import sqlite3
import os
from datetime import datetime

class StudentDatabase:
    def __init__(self, db_path="student_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with student table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                enrollment_number TEXT UNIQUE NOT NULL,
                face_encoding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                name TEXT,
                enrollment_number TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_student(self, name, enrollment_number, face_encoding):
        """Add a new student to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO students (name, enrollment_number, face_encoding)
                VALUES (?, ?, ?)
            ''', (name, enrollment_number, face_encoding))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Student with enrollment number {enrollment_number} already exists")
            return False
        finally:
            conn.close()
    
    def get_all_students(self):
        """Get all students from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, enrollment_number, face_encoding FROM students')
        students = cursor.fetchall()
        conn.close()
        
        return students
    
    def get_student_by_enrollment(self, enrollment_number):
        """Get student by enrollment number"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM students WHERE enrollment_number = ?', (enrollment_number,))
        student = cursor.fetchone()
        conn.close()
        
        return student
    
    def mark_attendance(self, student_id, name, enrollment_number):
        """Mark attendance for a student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO attendance (student_id, name, enrollment_number)
            VALUES (?, ?, ?)
        ''', (student_id, name, enrollment_number))
        
        conn.commit()
        conn.close()
    
    def get_attendance_records(self):
        """Get all attendance records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM attendance ORDER BY timestamp DESC')
        records = cursor.fetchall()
        conn.close()
        
        return records
    
    def delete_all_attendance(self):
        """Delete all attendance records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM attendance')
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def delete_all_students(self):
        """Delete all students and their attendance records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete attendance records first (foreign key constraint)
        cursor.execute('DELETE FROM attendance')
        attendance_deleted = cursor.rowcount
        
        # Delete students
        cursor.execute('DELETE FROM students')
        students_deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return students_deleted, attendance_deleted
    
    def get_attendance_count(self):
        """Get count of attendance records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM attendance')
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def get_student_count(self):
        """Get count of students"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM students')
        count = cursor.fetchone()[0]
        conn.close()
        
        return count


