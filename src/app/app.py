from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
)
from PyQt5.QtCore import Qt


from src.app.worker import Worker
from src.app.jobbox import JobDetailsDialog

from src.profiles import ProfileManager
from src.utils import Agent
from src.scraper import Job



class JobApplicationGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.agent = Agent()
        self.all_profiles = ProfileManager()
        self.worker = None  # Attribute to hold the thread
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Job Application Bot")
        self.setGeometry(100, 100, 1000, 600)
        layout = QVBoxLayout()

        self.jobInput = QLineEdit(self)
        self.jobInput.setPlaceholderText("Enter job URL or keyword...")

        self.searchButton = QPushButton("Start Job Search", self)
        self.searchButton.clicked.connect(self.start_search)

        self.statusLabel = QLabel("Status: Idle", self)  # To show current status
        self.cancelButton = QPushButton("Cancel Search", self)
        self.cancelButton.clicked.connect(self.cancel_search)
        self.cancelButton.setEnabled(False)  # Disabled until a search is active

        self.jobList = QListWidget(self)
        self.jobList.itemClicked.connect(self.display_job_details)

        layout.addWidget(self.statusLabel)
        layout.addWidget(self.cancelButton)

        layout.addWidget(QLabel("Job URL or Keyword:"))
        layout.addWidget(self.jobInput)
        layout.addWidget(self.searchButton)
        layout.addWidget(self.jobList)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

    def start_search(self):
        self.searchButton.setEnabled(False)
        self.cancelButton.setEnabled(True)
        self.statusLabel.setText("Status: Starting search...")
        self.worker = Worker(self.agent, self.jobInput.text(), self.all_profiles)
        self.worker.finished.connect(self.on_search_complete)
        self.worker.update_status.connect(self.update_status)
        self.worker.canceled.connect(self.on_search_canceled)
        self.worker.start()

    def update_status(self, message: str, job: Job):
        self.statusLabel.setText(f"Status: {message}")
        item = QListWidgetItem(f"{job.position} at {job.company}")
        item.setData(Qt.UserRole, job)
        self.jobList.addItem(item)

    def cancel_search(self):
        if self.worker is not None:
            self.worker.stop()
            self.statusLabel.setText("Search canceled.")
            self.searchButton.setEnabled(True)
            self.cancelButton.setEnabled(False)

    def on_search_canceled(self):
        self.statusLabel.setText("Status: Search canceled.")
        self.searchButton.setEnabled(True)
        self.cancelButton.setEnabled(False)

    def on_search_complete(self):
        self.statusLabel.setText("Status: Search complete.")
        self.searchButton.setEnabled(True)
        self.cancelButton.setEnabled(False)

    def display_job_details(self, item):
        job = item.data(Qt.UserRole)
        dialog = JobDetailsDialog(job)
        dialog.exec_()
