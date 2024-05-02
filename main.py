import sys

from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication

from src.app.app import JobApplicationGUI


load_dotenv()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = JobApplicationGUI()
    ex.show()
    sys.exit(app.exec())