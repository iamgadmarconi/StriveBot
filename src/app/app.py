from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
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
    QMessageBox,
)
from PyQt5.QtCore import Qt


from src.app.worker import Worker, MatchingWorker
from src.app.jobbox import JobDetailsDialog
from src.app.utils import CustomListWidget

from src.profiles import ProfileManager
from src.utils import Agent
from src.scraper import Job
from src.save import save_job_to_csv
from src.agent import get_profiles_from_match


class JobApplicationGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.agent = Agent()
        self.all_profiles = ProfileManager()
        self.dialogs = {}  # Store dialogs for each job
        self.worker = None  # Attribute to hold the thread
        self.initUI(layout)

    def initUI(self, layout):
        self.setWindowTitle("StriiveBot")
        self.setGeometry(100, 100, 1000, 600)

        layout.addWidget(QLabel("Job URL or Keyword:"))

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self.jobInput = QLineEdit(self)
        self.jobInput.setPlaceholderText("Enter job URL or keyword...")
        layout.addWidget(self.jobInput)

        self.searchButton = QPushButton("Start Job Search", self)
        self.searchButton.clicked.connect(self.start_search)
        layout.addWidget(self.searchButton)

        self.pauseButton = QPushButton('Pause', self)
        self.resumeButton = QPushButton('Resume', self)
        self.cancelButton = QPushButton('Cancel', self)

        self.statusLabel = QLabel("Status: Idle", self)  # To show current status
        layout.addWidget(self.statusLabel)

        self.resumeButton.setEnabled(False)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.pauseButton)
        buttonLayout.addWidget(self.resumeButton)
        buttonLayout.addWidget(self.cancelButton)

        # Add button layout to main layout
        layout.addLayout(buttonLayout)

        # Connect buttons to their respective functions
        self.pauseButton.clicked.connect(self.pause_search)
        self.resumeButton.clicked.connect(self.resume_search)
        self.cancelButton.clicked.connect(self.cancel_search)     

        self.jobList = CustomListWidget(self)
        self.jobList.itemClicked.connect(self.display_job_details)
        self.jobList.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.jobList)

        self.exportButton = QPushButton("Export to CSV", self)
        self.matchButton = QPushButton("Match Candidates", self)

        self.exportButton.clicked.connect(self.exportJobs)
        self.matchButton.clicked.connect(self.matchJobs)

        layout.addWidget(self.exportButton)
        layout.addWidget(self.matchButton)

    def exportJobs(self):
        jobs = [self.jobList.item(i).data(Qt.UserRole) for i in range(self.jobList.count())
                if self.jobList.item(i).checkState() == Qt.Checked]
        if jobs:
            for job in jobs:
                save_job_to_csv(job)  # Assuming this function exists
            QMessageBox.information(self, "Export Complete", "Selected jobs have been exported to CSV.")
        else:
            QMessageBox.information(self, "No Selection", "Please select one or more jobs to export.")

    def matchJobs(self):
        jobs = [self.jobList.item(i).data(Qt.UserRole) for i in range(self.jobList.count())
                if self.jobList.item(i).checkState() == Qt.Checked]
        if jobs:
            self.matchingWorker = MatchingWorker(self.agent, self.all_profiles, jobs)
            self.matchingWorker.profiles_found.connect(self.populate_candidates_tab)
            self.matchingWorker.error.connect(self.show_error)
            self.matchingWorker.start()
        else:
            QMessageBox.information(self, "No Selection", "Please select one or more jobs for matching.")

    def populate_candidates_tab(self, candidates, job):
        dialog = self.get_job_dialog(job)
        if dialog:
            dialog.candidateList.clear()
            for candidate in candidates:
                item = QListWidgetItem(f"{candidate.name} - {candidate.skills}")
                item.setData(Qt.UserRole, candidate)
                dialog.candidateList.addItem(item)

    def get_job_dialog(self, job):
        # Manage or instantiate a dialog for a specific job
        if job.id not in self.dialogs:
            self.dialogs[job.id] = JobDetailsDialog(job)
        return self.dialogs[job.id]

    def show_error(self, message):
        QMessageBox.critical(self, "Error", f"An error occurred during matching:\n{message}")

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
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.Unchecked)
        self.jobList.addItem(item)

    def cancel_search(self):
        if self.worker is not None:
            self.worker.stop()
            self.statusLabel.setText("Search canceled.")
            self.searchButton.setEnabled(True)
            self.cancelButton.setEnabled(False)

    def on_paused(self, is_paused):
            # Slot to update the GUI when paused/resumed
            if is_paused:
                self.statusLabel.setText('Status: Paused.')
                self.pauseButton.setEnabled(False)
                self.resumeButton.setEnabled(True)
            else:
                self.statusLabel.setText('Status: Running...')
                self.pauseButton.setEnabled(True)
                self.resumeButton.setEnabled(False)

    def pause_search(self):
        if self.worker is not None:
            self.worker.pause()
            self.pauseButton.setEnabled(False)
            self.resumeButton.setEnabled(True)
            self.cancelButton.setEnabled(True)

    def resume_search(self):
        if self.worker is not None:
            self.worker.resume()
            self.pauseButton.setEnabled(True)
            self.resumeButton.setEnabled(False)
            self.cancelButton.setEnabled(True)

    def on_search_canceled(self):
        self.statusLabel.setText("Status: Search canceled.")
        self.searchButton.setEnabled(True)
        self.cancelButton.setEnabled(False)
        self.pauseButton.setEnabled(False)
        self.resumeButton.setEnabled(False)

    def on_search_complete(self):
        self.statusLabel.setText("Status: Search complete.")
        self.searchButton.setEnabled(True)
        self.cancelButton.setEnabled(False)
        self.pauseButton.setEnabled(False)
        self.resumeButton.setEnabled(False)

    def display_job_details(self, item):
        job = item.data(Qt.UserRole)
        dialog = JobDetailsDialog(job)
        dialog.exec_()
