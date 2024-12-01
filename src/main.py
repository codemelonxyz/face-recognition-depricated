from PyQt6.QtWidgets import QApplication
import sys
from gui import FaceRecognitionApp
from database import Database

if __name__ == "__main__":
    # Initialize the database to create tables
    db = Database()
    
    app = QApplication(sys.argv)
    window = FaceRecognitionApp()
    window.show()
    sys.exit(app.exec())
