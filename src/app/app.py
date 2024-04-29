from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QTextEdit,
    QLabel,
)

from src.profiles import ProfileManager
from src.utils import Agent, pretty_print_matches
from src.scraper import Job, get_jobs
from src.agent import motivation_letter, profile_matcher, profile_from_names
from src.save import save_job_to_csv


class JobApplicationGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.agent = Agent()
        self.all_profiles = ProfileManager()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Job Application Bot")
        self.setGeometry(100, 100, 1000, 600)
        layout = QVBoxLayout()

        # Job URL input
        self.jobInput = QLineEdit(self)
        self.jobInput.setPlaceholderText("Enter job URL or keywords...")

        # Search Button
        self.searchButton = QPushButton("Start Job Search", self)
        self.searchButton.clicked.connect(self.start_search)

        # Results Display
        self.resultsDisplay = QTextEdit(self)
        self.resultsDisplay.setReadOnly(True)

        layout.addWidget(QLabel("Job URL:"))
        layout.addWidget(self.jobInput)
        layout.addWidget(self.searchButton)
        layout.addWidget(QLabel("Results:"))
        layout.addWidget(self.resultsDisplay)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

    def start_single_search(self, url: str):
        job = Job(self.agent, url)

    # def start_search(self):
    #     url = self.jobInput.text()
    #     job = Job(self.agent, url, "Position", "Company")  # Simplified for the example
    #     jobs = [job]  # Simulate a single job fetch
    #     matches = []
    #     for job in jobs:
    #         profiles = profile_matcher(self.agent, self.all_profiles, job)
    #         if profiles:
    #             profile_obj = profile_from_names(profiles)
    #             for profile in profile_obj:
    #                 motivation = motivation_letter(self.agent, profile, job)
    #                 job.candidates = (profile, motivation)
    #                 profile.add_job_match(job, motivation)
    #                 data = {
    #                     "Position": job.position,
    #                     "Company": job.company,
    #                     "Candidate": profile,
    #                     "Motivation": motivation,
    #                 }
    #                 self.resultsDisplay.append(pretty_print_matches(data))
    #                 matches.append(data)
    #                 save_job_to_csv(job, force=True)
    #     return matches

