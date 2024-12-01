from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from database import Database
from datetime import datetime
import numpy as np  # Add this import if not already present
import cv2
import face_recognition

class AdminPortal(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db  # Use the passed Database instance
        self.setWindowTitle("Admin Portal")
        self.setGeometry(200, 200, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Class Schedule Form
        schedule_group = QGroupBox("Schedule New Class")
        schedule_layout = QFormLayout()
        
        self.subject_input = QLineEdit()
        self.date_input = QDateEdit(calendarPopup=True)
        self.start_time = QTimeEdit()
        self.end_time = QTimeEdit()
        
        schedule_layout.addRow("Subject:", self.subject_input)
        schedule_layout.addRow("Date:", self.date_input)
        schedule_layout.addRow("Start Time:", self.start_time)
        schedule_layout.addRow("End Time:", self.end_time)
        
        schedule_btn = QPushButton("Schedule Class")
        schedule_btn.clicked.connect(self.schedule_class)
        schedule_layout.addRow(schedule_btn)
        
        schedule_group.setLayout(schedule_layout)
        layout.addWidget(schedule_group)
        
        # Attendance View
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(4)
        self.attendance_table.setHorizontalHeaderLabels(["Student", "Subject", "Date", "Time"])
        layout.addWidget(self.attendance_table)
        
        self.load_attendance()
        
        # Optional: Add Student Management
        student_group = QGroupBox("Manage Students")
        student_layout = QFormLayout()
        
        self.student_name_input = QLineEdit()
        student_layout.addRow("Name:", self.student_name_input)
        
        add_student_btn = QPushButton("Add Student")
        add_student_btn.clicked.connect(self.add_student)
        student_layout.addRow(add_student_btn)
        
        student_group.setLayout(student_layout)
        layout.addWidget(student_group)
        
    def schedule_class(self):
        subject = self.subject_input.text()
        date = self.date_input.date().toPyDate()
        start = self.start_time.time().toPyTime()
        end = self.end_time.time().toPyTime()
        
        start_datetime = datetime.combine(date, start)
        end_datetime = datetime.combine(date, end)
        
        if start_datetime >= end_datetime:
            QMessageBox.warning(self, "Error", "End time must be after start time.")
            return
        
        self.db.cursor.execute("""
            INSERT INTO classes (subject, start_time, end_time)
            VALUES (%s, %s, %s)
        """, (subject, start_datetime, end_datetime))
        self.db.connection.commit()
        
        QMessageBox.information(self, "Success", "Class scheduled successfully!")
        self.load_attendance()
        
    def load_attendance(self):
        self.db.cursor.execute("""
            SELECT s.name, c.subject, a.timestamp
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            JOIN classes c ON a.class_id = c.id
            ORDER BY a.timestamp DESC
        """)
        records = self.db.cursor.fetchall()
        
        self.attendance_table.setRowCount(len(records))
        for i, record in enumerate(records):
            self.attendance_table.setItem(i, 0, QTableWidgetItem(record[0]))
            self.attendance_table.setItem(i, 1, QTableWidgetItem(record[1]))
            self.attendance_table.setItem(i, 2, QTableWidgetItem(record[2].strftime("%Y-%m-%d")))
            self.attendance_table.setItem(i, 3, QTableWidgetItem(record[2].strftime("%H:%M")))

    def add_student(self):
        name = self.student_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a valid name.")
            return
        
        # Capture a face encoding properly instead of using zeros
        # This requires implementing a method to get the face encoding, possibly from a captured image
        success, face_encoding = self.capture_face_encoding()  # Implement this method
        if not success:
            QMessageBox.warning(self, "Error", "Failed to capture face encoding.")
            return
        
        success = self.db.insert_student(name, face_encoding)
        if success:
            QMessageBox.information(self, "Success", f"Student '{name}' added successfully.")
            self.student_name_input.clear()
            self.load_attendance()
        else:
            QMessageBox.warning(self, "Error", "Failed to add student.")
    
    def capture_face_encoding(self):
        """
        Captures a single frame from the camera and returns the face encoding.
        Returns:
            (bool, np.ndarray): Success status and the face encoding.
        """
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return False, None
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return False, None
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        if len(face_encodings) != 1:
            return False, None
        
        return True, face_encodings[0]