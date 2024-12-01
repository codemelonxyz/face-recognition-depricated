from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox
)
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtCore import QTimer
import cv2
# Removed direct imports of face_recognition and numpy
# import face_recognition
# import numpy as np
from face_recognition_module import load_known_faces, recognize_faces, register_face  # Added 'register_face'

class FaceRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Recognition System")
        self.setGeometry(100, 100, 1024, 768)

        # Initialize variables
        self.known_face_encodings, self.known_face_names = load_known_faces()
        self.camera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)

        # Set up tabs
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        # Main recognition tab
        self.recognition_tab = QWidget()
        self.tabs.addTab(self.recognition_tab, "Face Recognition")
        self.setup_recognition_ui()

        # Face registration tab
        self.registration_tab = QWidget()
        self.tabs.addTab(self.registration_tab, "Register Faces")
        self.setup_registration_ui()

        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QLabel#status_label, QLabel#face_load_status {
                color: #ecf0f1;
                font-size: 16px;
            }
            QLabel#instruction_label {
                color: #ecf0f1;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2980b9;
                color: #ecf0f1;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QTabWidget::pane {
                border-top: 2px solid #34495e;
            }
            QTabBar::tab {
                background: #34495e;
                color: #ecf0f1;
                padding: 10px;
            }
            QTabBar::tab:selected {
                background: #2c3e50;
            }
        """)

    def setup_recognition_ui(self):
        layout = QVBoxLayout(self.recognition_tab)

        # Status label
        self.status_label = QLabel("System Ready - No Camera Active", objectName="status_label")
        layout.addWidget(self.status_label)

        # Video feed
        self.video_label = QLabel()
        self.video_label.setFixedSize(800, 600)
        layout.addWidget(self.video_label)

        # Buttons
        self.start_button = QPushButton("Start Camera")
        self.start_button.clicked.connect(self.start_camera)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.clicked.connect(self.stop_camera)
        layout.addWidget(self.stop_button)

    def setup_registration_ui(self):
        layout = QVBoxLayout(self.registration_tab)

        # Instructions
        instruction_label = QLabel(
            "To register a new face, click 'Capture Face' while the camera is active.",
            objectName="instruction_label"
        )
        layout.addWidget(instruction_label)

        # Capture face button
        self.capture_button = QPushButton("Capture Face")
        self.capture_button.clicked.connect(self.capture_face)
        layout.addWidget(self.capture_button)

        # Faces loaded status
        self.face_load_status = QLabel("No faces registered yet.", objectName="face_load_status")
        layout.addWidget(self.face_load_status)

    def start_camera(self):
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            QMessageBox.critical(self, "Error", "Could not access the camera")
            self.status_label.setText("Error: Camera initialization failed")
            return
        self.status_label.setText("Camera Active - Detecting Faces")
        self.timer.start(30)

    def stop_camera(self):
        if self.camera is not None:
            self.timer.stop()
            self.camera.release()
            self.camera = None
            self.video_label.clear()
        self.status_label.setText("System Ready - No Camera Active")

    def update_camera(self):
        if self.camera is not None:
            ret, frame = self.camera.read()
            if not ret:
                self.stop_camera()
                return

            # Use recognize_faces function from face_recognition_module
            annotated_frame = recognize_faces(frame, self.known_face_encodings, self.known_face_names)

            # Display the frame in the QLabel
            rgb_image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.video_label.setPixmap(pixmap)

    def capture_face(self):
        if self.camera is None:
            QMessageBox.warning(self, "Warning", "Please start the camera first!")
            return

        ret, frame = self.camera.read()
        if ret:
            # Use register_face function from face_recognition_module
            face_image, message = register_face(frame)
            if face_image is None:
                QMessageBox.warning(self, "Error", message)
                return

            name, ok = QFileDialog.getSaveFileName(
                self,
                "Save New Face",
                "known_faces/",
                "Images (*.jpg *.jpeg *.png)"
            )
            if ok:
                cv2.imwrite(name, face_image)
                # Load and encode the new face using face_recognition_module
                success = register_new_face(name)
                if success:
                    self.face_load_status.setText(f"Registered {len(self.known_face_names)} faces.")
                    QMessageBox.information(self, "Success", "New face registered successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to encode face. Please try again.")