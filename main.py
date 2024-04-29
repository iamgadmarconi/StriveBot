import sys

from PyQt5.QtWidgets import QApplication
from dotenv import load_dotenv

from src.app.app import JobApplicationGUI


load_dotenv()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = JobApplicationGUI()
    ex.show()
    sys.exit(app.exec_())