import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
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


from src.app.worker import Worker, MatchingWorker
from src.app.windows import JobDetailsDialog
from src.app.utils import CustomListWidget

from src.profiles import ProfileManager
from src.utils import Agent, get_base_path
from src.scraper import Job
from src.save import save_job_to_csv
from src.db.db import JobDAO, CandidateDAO, MatchDAO


class JobApplicationGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.agent = Agent()
        self.jobdao = JobDAO()
        self.candidatedao = CandidateDAO()
        self.matchdao = MatchDAO()
        self.all_profiles = ProfileManager()
        for candidate in self.all_profiles.profiles:
            self.candidatedao.add_candidate(candidate)

        self.dialogs = {}  # Store dialogs for each job
        self.worker = None  # Attribute to hold the thread
        self.child_windows = []
        self.initUI(layout)

    def initUI(self, layout):
        self.setWindowTitle("StriiveBot")
        self.setGeometry(100, 100, 1000, 600)
        icon_path = os.path.join(get_base_path(), 'app\\static', 'ai.png')
        # print(icon_path)
        self.setWindowIcon(QIcon(icon_path))

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
        self.pauseButton.setEnabled(False)
        self.cancelButton.setEnabled(False)
        self.resumeButton.setEnabled(False)

        self.jobList = CustomListWidget(self)
        self.jobList.itemClicked.connect(self.display_job_details)
        self.jobList.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.jobList)
        # Load jobs from the database
        self.load_jobs()

        self.exportButton = QPushButton("Export to CSV", self)
        self.matchButton = QPushButton("Match Candidates", self)

        self.exportButton.clicked.connect(self.exportJobs)
        self.matchButton.clicked.connect(self.matchJobs)

        layout.addWidget(self.exportButton)
        layout.addWidget(self.matchButton)

    def exportJobs(self):
        jobs = [self.jobList.item(i).data(Qt.UserRole) for i in range(self.jobList.count())
                if self.jobList.item(i).checkState() == Qt.CheckState.Checked]
        if jobs:
            for job in jobs:
                save_job_to_csv(job) 
            QMessageBox.information(self, "Export Complete", "Selected jobs have been exported to CSV.")
        else:
            QMessageBox.information(self, "No Selection", "Please select one or more jobs to export.")

    def matchJobs(self):
        self.matchButton.setEnabled(False)
        self.matchButton.setText("Matching...")
        jobs = [self.jobList.item(i).data(Qt.UserRole) for i in range(self.jobList.count())
                if self.jobList.item(i).checkState() == Qt.CheckState.Checked]
        if jobs:
            self.matchingWorker = MatchingWorker(self.agent, self.all_profiles, jobs, self.jobdao, self.matchdao)
            self.matchingWorker.profiles_found.connect(self.populate_candidates_tab)
            self.matchingWorker.completed.connect(self.on_match_complete)
            self.matchingWorker.error.connect(self.show_error)
            self.matchingWorker.start()
        else:
            QMessageBox.information(self, "No Selection", "Please select one or more jobs for matching.")
            self.matchButton.setText("Match Candidates")
            self.matchButton.setEnabled(True)

    def on_match_complete(self, message):
        self.matchButton.setText("Match Candidates")
        self.matchButton.setEnabled(True)
        QMessageBox.information(self, "Matching Complete", message)

    def populate_candidates_tab(self, candidates, job):
        dialog = self.get_job_dialog(job)
        if dialog:
            dialog.candidateList.clear()  # Clear existing entries
            for candidate in candidates:
                item = QListWidgetItem(candidate.name)
                item.setData(Qt.UserRole, candidate)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item.setCheckState(Qt.CheckState.Unchecked)
                dialog.candidateList.addItem(item)
            # Do not show or activate the dialog here
            print(f"Candidates updated for job {job.position} in background.")  # Optional debug

    def get_job_dialog(self, job):
        if job.id not in self.dialogs:
            self.dialogs[job.id] = JobDetailsDialog(self, job, self.candidatedao, self.matchdao)
        return self.dialogs[job.id]

    def show_error(self, message):
        self.matchButton.setText("Match Candidates")
        self.matchButton.setEnabled(True)
        QMessageBox.critical(self, "Error", f"An error occurred during matching:\n{message}")

    def start_search(self):
        self.resumeButton.setEnabled(False)
        self.searchButton.setEnabled(False)
        self.cancelButton.setEnabled(True)
        self.pauseButton.setEnabled(True)
        if self.jobInput.text() == "":
            self.statusLabel.setText("Status: Searching...")
        else:
            self.statusLabel.setText(f"Status: Searching with keyword '{self.jobInput.text()[:12]}...'")
        self.worker = Worker(self.agent, self.jobInput.text(), self.all_profiles, self.jobdao)
        self.worker.finished.connect(self.on_search_complete)
        self.worker.update_status.connect(self.update_status)
        self.worker.canceled.connect(self.on_search_canceled)
        self.worker.start()

    def update_status(self, message: str, job: Job):
        self.statusLabel.setText(f"{message}")
        item = QListWidgetItem(f"{job.position} at {job.company}")
        item.setData(Qt.UserRole, job)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.CheckState.Unchecked)
        self.jobList.addItem(item)

    def cancel_search(self):
        if self.worker is not None:
            self.worker.stop()
            self.statusLabel.setText("Search canceled.")
            self.searchButton.setEnabled(True)
            self.cancelButton.setEnabled(False)

    def on_paused(self, is_paused):
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
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        dialog = self.get_job_dialog(job)
        if not dialog:
            dialog = JobDetailsDialog(self, job, self.candidatedao, self.matchdao)
            self.dialogs[job.id] = dialog

        self.child_windows.append(dialog)
        dialog.show()

    def load_jobs(self):
        try:
            jobs = self.jobdao.list_all_jobs()
            for job in jobs:
                self.add_job_to_list(job)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load jobs from database:\n{str(e)}")

    def add_job_to_list(self, job):
        item = QListWidgetItem(f"{job.position} at {job.company}")
        item.setData(Qt.UserRole, job)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.CheckState.Unchecked)
        self.jobList.addItem(item)

    def closeEvent(self, event):
            for window in self.child_windows:
                window.close()  # Ensure all child windows are closed
            event.accept()