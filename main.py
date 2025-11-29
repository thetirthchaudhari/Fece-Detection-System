import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import cv2
from face_recognition_system import FaceRecognitionSystem
from excel_export import ExcelExporter
from database import StudentDatabase
import threading
from datetime import datetime

class AttendanceSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("800x600")
        
        # Initialize components
        self.face_system = FaceRecognitionSystem()
        self.excel_exporter = ExcelExporter()
        self.db = StudentDatabase()
        
        # Create GUI elements
        self.create_widgets()
        
        # Flag for recognition thread
        self.recognition_running = False
        self.recognition_thread = None
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Title
        title_label = tk.Label(self.root, text="Face Recognition Attendance System", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Student Management Section
        student_frame = ttk.LabelFrame(main_frame, text="Student Management", padding=10)
        student_frame.pack(fill="x", pady=(0, 10))
        
        # Add student button
        add_student_btn = ttk.Button(student_frame, text="Add New Student", 
                                   command=self.add_student)
        add_student_btn.pack(side="left", padx=(0, 10))
        
        # View students button
        view_students_btn = ttk.Button(student_frame, text="View Students", 
                                     command=self.view_students)
        view_students_btn.pack(side="left", padx=(0, 10))
        
        # Attendance Section
        attendance_frame = ttk.LabelFrame(main_frame, text="Attendance System", padding=10)
        attendance_frame.pack(fill="x", pady=(0, 10))
        
        # Start recognition button
        self.start_btn = ttk.Button(attendance_frame, text="Start Recognition", 
                                  command=self.start_recognition)
        self.start_btn.pack(side="left", padx=(0, 10))
        
        # Stop recognition button
        self.stop_btn = ttk.Button(attendance_frame, text="Stop Recognition", 
                                 command=self.stop_recognition, state="disabled")
        self.stop_btn.pack(side="left", padx=(0, 10))
        
        # Export Section
        export_frame = ttk.LabelFrame(main_frame, text="Export & Reports", padding=10)
        export_frame.pack(fill="x", pady=(0, 10))
        
        # Export all attendance button
        export_all_btn = ttk.Button(export_frame, text="Export All Attendance", 
                                  command=self.export_all_attendance)
        export_all_btn.pack(side="left", padx=(0, 10))
        
        # Export daily attendance button
        export_daily_btn = ttk.Button(export_frame, text="Export Daily Attendance", 
                                    command=self.export_daily_attendance)
        export_daily_btn.pack(side="left", padx=(0, 10))
        
        # View attendance summary button
        summary_btn = ttk.Button(export_frame, text="View Summary", 
                               command=self.view_attendance_summary)
        summary_btn.pack(side="left", padx=(0, 10))
        
        # Data Management Section
        data_frame = ttk.LabelFrame(main_frame, text="Data Management", padding=10)
        data_frame.pack(fill="x", pady=(0, 10))
        
        # Delete attendance button
        delete_attendance_btn = ttk.Button(data_frame, text="Delete All Attendance", 
                                         command=self.delete_all_attendance)
        delete_attendance_btn.pack(side="left", padx=(0, 10))
        
        # Delete all data button
        delete_all_btn = ttk.Button(data_frame, text="Delete All Data", 
                                  command=self.delete_all_data)
        delete_all_btn.pack(side="left", padx=(0, 10))
        
        # Status Section
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding=10)
        status_frame.pack(fill="both", expand=True)
        
        # Status text
        self.status_text = tk.Text(status_frame, height=10, wrap="word")
        scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Initial status
        self.update_status("System initialized. Ready to start.")
    
    def update_status(self, message):
        """Update the status text"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def add_student(self):
        """Add a new student to the system"""
        # Get student details
        name = simpledialog.askstring("Add Student", "Enter student name:")
        if not name:
            return
        
        enrollment = simpledialog.askstring("Add Student", "Enter enrollment number:")
        if not enrollment:
            return
        
        # Check if enrollment already exists
        existing = self.db.get_student_by_enrollment(enrollment)
        if existing:
            messagebox.showerror("Error", f"Student with enrollment number {enrollment} already exists!")
            return
        
        # Capture face
        self.update_status(f"Capturing face for {name} ({enrollment})")
        success = self.face_system.capture_face(enrollment, name)
        
        if success:
            messagebox.showinfo("Success", f"Student {name} added successfully!")
            self.update_status(f"Student {name} ({enrollment}) added successfully")
        else:
            messagebox.showerror("Error", "Failed to capture face. Please try again.")
            self.update_status(f"Failed to add student {name}")
    
    def view_students(self):
        """View all students in the system"""
        students = self.db.get_all_students()
        
        if not students:
            messagebox.showinfo("Info", "No students found in the system.")
            return
        
        # Create new window to display students
        students_window = tk.Toplevel(self.root)
        students_window.title("Students List")
        students_window.geometry("600x400")
        
        # Create treeview
        tree = ttk.Treeview(students_window, columns=("ID", "Name", "Enrollment"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Name", text="Name")
        tree.heading("Enrollment", text="Enrollment Number")
        
        tree.column("ID", width=50)
        tree.column("Name", width=200)
        tree.column("Enrollment", width=150)
        
        # Add students to treeview
        for student in students:
            tree.insert("", "end", values=(student[0], student[1], student[2]))
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(students_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
    
    def start_recognition(self):
        """Start face recognition system"""
        if self.recognition_running:
            return
        
        self.recognition_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        self.update_status("Starting face recognition system...")
        
        # Start recognition in separate thread
        self.recognition_thread = threading.Thread(target=self.run_recognition)
        self.recognition_thread.daemon = True
        self.recognition_thread.start()
    
    def stop_recognition(self):
        """Stop face recognition system"""
        self.recognition_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        self.update_status("Face recognition system stopped.")
        
        # Close any open CV windows
        cv2.destroyAllWindows()
    
    def run_recognition(self):
        """Run face recognition system"""
        try:
            self.face_system.detect_and_recognize()
        except Exception as e:
            self.update_status(f"Error in recognition: {str(e)}")
        finally:
            self.recognition_running = False
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
    
    def export_all_attendance(self):
        """Export all attendance records to Excel"""
        self.update_status("Exporting all attendance records...")
        filename = self.excel_exporter.export_attendance_to_excel()
        
        if filename:
            messagebox.showinfo("Success", f"Attendance records exported to {filename}")
            self.update_status(f"Exported attendance to {filename}")
        else:
            messagebox.showerror("Error", "Failed to export attendance records.")
            self.update_status("Failed to export attendance records")
    
    def export_daily_attendance(self):
        """Export daily attendance records"""
        date = simpledialog.askstring("Export Daily Attendance", 
                                    "Enter date (YYYY-MM-DD) or leave empty for today:")
        
        if date is None:  # User cancelled
            return
        
        if not date:  # Empty string, use today
            date = datetime.now().strftime('%Y-%m-%d')
        
        self.update_status(f"Exporting daily attendance for {date}...")
        filename = self.excel_exporter.export_daily_attendance(date)
        
        if filename:
            messagebox.showinfo("Success", f"Daily attendance exported to {filename}")
            self.update_status(f"Exported daily attendance to {filename}")
        else:
            messagebox.showinfo("Info", f"No attendance records found for {date}")
            self.update_status(f"No records found for {date}")
    
    def view_attendance_summary(self):
        """View attendance summary"""
        summary = self.excel_exporter.get_attendance_summary()
        messagebox.showinfo("Attendance Summary", summary)
        self.update_status("Viewed attendance summary")
    
    def delete_all_attendance(self):
        """Delete all attendance records"""
        # Get current counts
        attendance_count = self.db.get_attendance_count()
        student_count = self.db.get_student_count()
        
        if attendance_count == 0:
            messagebox.showinfo("Info", "No attendance records to delete.")
            return
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete all {attendance_count} attendance records?\n\n"
                                   f"This will NOT delete the {student_count} enrolled students.")
        
        if result:
            deleted_count = self.db.delete_all_attendance()
            messagebox.showinfo("Success", f"Deleted {deleted_count} attendance records.")
            self.update_status(f"Deleted {deleted_count} attendance records")
            
            # Reload known faces to update the system
            self.face_system.load_known_faces()
    
    def delete_all_data(self):
        """Delete all students and attendance records"""
        # Get current counts
        attendance_count = self.db.get_attendance_count()
        student_count = self.db.get_student_count()
        
        if attendance_count == 0 and student_count == 0:
            messagebox.showinfo("Info", "No data to delete.")
            return
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete All", 
                                   f"Are you sure you want to delete ALL data?\n\n"
                                   f"This will delete:\n"
                                   f"- {student_count} students\n"
                                   f"- {attendance_count} attendance records\n\n"
                                   f"This action cannot be undone!")
        
        if result:
            students_deleted, attendance_deleted = self.db.delete_all_students()
            messagebox.showinfo("Success", 
                              f"Deleted all data:\n"
                              f"- {students_deleted} students\n"
                              f"- {attendance_deleted} attendance records")
            self.update_status(f"Deleted all data: {students_deleted} students, {attendance_deleted} attendance records")
            
            # Clear known faces from memory
            self.face_system.known_faces = {}
            self.face_system.known_encodings = []
            self.face_system.known_names = []
            self.face_system.known_enrollments = []
            self.face_system.recent_attendance = {}

def main():
    root = tk.Tk()
    app = AttendanceSystemGUI(root)
    
    # Handle window close
    def on_closing():
        if app.recognition_running:
            app.stop_recognition()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()