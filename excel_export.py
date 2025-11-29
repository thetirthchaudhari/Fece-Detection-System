import pandas as pd
from datetime import datetime
import os
from database import StudentDatabase

class ExcelExporter:
    def __init__(self):
        self.db = StudentDatabase()
    
    def export_attendance_to_excel(self, filename=None):
        """Export attendance records to Excel file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"attendance_records_{timestamp}.xlsx"
        
        # Get attendance records from database
        records = self.db.get_attendance_records()
        
        if not records:
            print("No attendance records found.")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(records, columns=[
            'ID', 'Student_ID', 'Name', 'Enrollment_Number', 'Timestamp'
        ])
        
        # Format timestamp
        df['Timestamp'] = pd.to_datetime(df['Timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Create Excel file
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Attendance Records', index=False)
                
                # Get worksheet to format
                worksheet = writer.sheets['Attendance Records']
                
                # Adjust column widths
                worksheet.column_dimensions['A'].width = 8   # ID
                worksheet.column_dimensions['B'].width = 12  # Student_ID
                worksheet.column_dimensions['C'].width = 25  # Name
                worksheet.column_dimensions['D'].width = 20  # Enrollment_Number
                worksheet.column_dimensions['E'].width = 20  # Timestamp
            
            print(f"Attendance records exported to {filename}")
            return filename
            
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return None
    
    def export_daily_attendance(self, date=None):
        """Export attendance for a specific date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        records = self.db.get_attendance_records()
        
        # Filter records for specific date
        daily_records = []
        for record in records:
            record_date = record[4].split(' ')[0]  # Extract date part
            if record_date == date:
                daily_records.append(record)
        
        if not daily_records:
            print(f"No attendance records found for {date}")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(daily_records, columns=[
            'ID', 'Student_ID', 'Name', 'Enrollment_Number', 'Timestamp'
        ])
        
        # Format timestamp
        df['Timestamp'] = pd.to_datetime(df['Timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Create Excel file
        filename = f"daily_attendance_{date}.xlsx"
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=f'Attendance_{date}', index=False)
                
                # Get worksheet to format
                worksheet = writer.sheets[f'Attendance_{date}']
                
                # Adjust column widths
                worksheet.column_dimensions['A'].width = 8   # ID
                worksheet.column_dimensions['B'].width = 12  # Student_ID
                worksheet.column_dimensions['C'].width = 25  # Name
                worksheet.column_dimensions['D'].width = 20  # Enrollment_Number
                worksheet.column_dimensions['E'].width = 20  # Timestamp
            
            print(f"Daily attendance records exported to {filename}")
            return filename
            
        except Exception as e:
            print(f"Error exporting daily attendance: {e}")
            return None
    
    def get_attendance_summary(self):
        """Get summary of attendance records"""
        records = self.db.get_attendance_records()
        
        if not records:
            return "No attendance records found."
        
        # Count unique students
        unique_students = len(set(record[1] for record in records if record[1]))
        
        # Count total attendance marks
        total_marks = len(records)
        
        # Get date range
        dates = [record[4].split(' ')[0] for record in records]
        date_range = f"{min(dates)} to {max(dates)}"
        
        summary = f"""
        Attendance Summary:
        - Total attendance marks: {total_marks}
        - Unique students: {unique_students}
        - Date range: {date_range}
        """
        
        return summary

