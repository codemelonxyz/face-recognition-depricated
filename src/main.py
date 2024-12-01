from PyQt6.QtWidgets import QApplication
import sys
from gui import FaceRecognitionApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceRecognitionApp()
    window.show()
    sys.exit(app.exec())
