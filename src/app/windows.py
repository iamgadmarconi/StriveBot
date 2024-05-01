from PyQt5.QtWidgets import (
    QDialog,
    QTabWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QGridLayout,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QScrollArea,
    QTextBrowser,
    QLineEdit,
)
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices, QColor, QIcon
from PyQt5.QtCore import QUrl

from src.utils import format_bulleted_list
from src.app.utils import CustomListWidget
from src.app.worker import MotivationWorker, MatchingWorker
from src.profiles import Profile
from src.db.db import CandidateModel


class JobDetailsDialog(QDialog):
    def __init__(self, parent, job, candidatedao, matchdao):
        super().__init__()
        self.par = parent
        self.agent = parent.agent
        self.job = job
        self._id = job.id
        self.candidatedao = candidatedao
        self.matchdao = matchdao
        self.candidate_dialogs = {}
        self.initUI()

    @property
    def id(self):
        return self._id

    def initUI(self):
        self.setWindowTitle("Job Details")
        self.setGeometry(100, 100, 600, 400)
        self.setMaximumWidth(800)  # Set initial size and position

        layout = QVBoxLayout(self)

        # Create the tab widget
        tabWidget = QTabWidget()
        tabWidget.addTab(self.create_main_tab(), "Main")
        tabWidget.addTab(self.create_calendar_tab(), "Calendar")
        tabWidget.addTab(self.create_contact_tab(), "Contact")
        tabWidget.addTab(self.create_assignment_tab(), "Assignment")
        tabWidget.addTab(self.create_candidates_tab(), "Candidates")
        self.load_matched_candidates()  

        layout.addWidget(tabWidget)

    def create_text_display_widget(self, text, bulleted=False):
        """Helper to create a text display widget that handles text wrapping."""
        textEdit = QTextEdit()
        formatted_text = format_bulleted_list(text) if bulleted else text
        textEdit.setText(formatted_text)
        textEdit.setReadOnly(True)
        textEdit.setWordWrapMode(True)
        return textEdit

    def create_main_tab(self):
        widget = QWidget()
        grid = QGridLayout()

        # Job position and company
        grid.addWidget(QLabel("Position:"), 0, 0)
        grid.addWidget(QLabel(self.job.position), 0, 1)
        grid.addWidget(QLabel("Company:"), 1, 0)
        grid.addWidget(QLabel(self.job.company), 1, 1)

        # Job URL
        urlButton = QPushButton("Open URL")
        urlButton.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.job.url)))
        grid.addWidget(QLabel("URL:"), 2, 0)
        grid.addWidget(urlButton, 2, 1)

        # Location and Max Hourly Rate
        grid.addWidget(QLabel("Location:"), 3, 0)
        grid.addWidget(QLabel(self.job.location), 3, 1)
        grid.addWidget(QLabel("Max Hourly Rate:"), 4, 0)
        grid.addWidget(QLabel(str(self.job.max_hourly_rate)), 4, 1)

        # Status with colored icon
        status_label = QLabel("Status:")
        status_icon = QLabel()
        if self.job.status == "Open":
            status_icon.setPixmap(QIcon(r"src\app\static\button.png").pixmap(15, 15))
        else:
            status_icon.setPixmap(QIcon(r"src\app\static\cross.png").pixmap(15, 15))
        grid.addWidget(status_label, 5, 0)
        grid.addWidget(status_icon, 5, 1)

        widget.setLayout(grid)
        return widget

    def create_calendar_tab(self):
        widget = QWidget()
        grid = QGridLayout()
        grid.addWidget(QLabel("Deadline:"), 0, 0)
        grid.addWidget(QLabel(self.job.deadline), 0, 1)
        grid.addWidget(QLabel("Start Date:"), 1, 0)
        grid.addWidget(QLabel(self.job.start), 1, 1)
        grid.addWidget(QLabel("End Date:"), 2, 0)
        grid.addWidget(QLabel(self.job.end), 2, 1)
        grid.addWidget(QLabel("Commitment:"), 3, 0)
        grid.addWidget(QLabel(self.job.commitment), 3, 1)
        widget.setLayout(grid)
        return widget

    def create_contact_tab(self):
        widget = QWidget()
        grid = QGridLayout()
        if self.job.submitter:
            grid.addWidget(QLabel("Name:"), 0, 0)
            grid.addWidget(QLabel(self.job.submitter.name), 0, 1)

            email_label = QLabel("Email:")
            grid.addWidget(email_label, 1, 0)

            # Add a clickable label for email
            email_address = QLabel('<a href="mailto:{}">{}</a>'.format(self.job.submitter.email, self.job.submitter.email))
            email_address.setTextFormat(Qt.RichText)  # Set text format to RichText for HTML links
            email_address.setTextInteractionFlags(Qt.TextBrowserInteraction)  # Allow label to handle links
            email_address.setOpenExternalLinks(True)  # Enable opening links in default browser
            grid.addWidget(email_address, 1, 1)

            grid.addWidget(QLabel("Phone Number:"), 2, 0)
            phone_number = QLabel('<a href="tel:{}">{}</a>'.format(self.job.submitter.phone, self.job.submitter.phone))
            phone_number.setOpenExternalLinks(True)  # Enable opening links in default browser
            phone_number.setTextInteractionFlags(Qt.TextBrowserInteraction)
            phone_number.setOpenExternalLinks(True)
            phone_number.setWordWrap(True)
            grid.addWidget(phone_number, 2, 1)

        widget.setLayout(grid)
        return widget

    def create_assignment_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        if self.job.assignment:

            layout.addWidget(QLabel("Requirements:"))
            requirementsWidget = self.create_text_display_widget(
                self.job.assignment.requirements, bulleted=True
            )
            layout.addWidget(requirementsWidget)

            layout.addWidget(QLabel("Skills:"))
            skillsWidget = self.create_text_display_widget(
                self.job.assignment.skills, bulleted=True
            )
            layout.addWidget(skillsWidget)

            layout.addWidget(QLabel("Preferences:"))
            preferencesWidget = self.create_text_display_widget(
                self.job.assignment.preferences, bulleted=True
            )
            layout.addWidget(preferencesWidget)
        widget.setLayout(layout)
        return widget

    def create_candidates_tab(self):
        self.widget = QWidget()
        layout = QVBoxLayout()
        self.candidateList = CustomListWidget(self)

        self.candidateList.itemClicked.connect(self.display_candidate_details)
        self.candidateList.setSelectionMode(QListWidget.MultiSelection)

        # Wrap the candidate list in a scroll area
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(self.candidateList)
        layout.addWidget(scrollArea)
        
        self.matchCandidatesButton = QPushButton("Match Candidates")
        self.matchCandidatesButton.clicked.connect(self.match_candidates)
        layout.addWidget(self.matchCandidatesButton)

        self.createMotivationButton = QPushButton("Create Motivation Letter")
        self.createMotivationButton.clicked.connect(self.create_motivations)
        layout.addWidget(self.createMotivationButton)

        self.widget.setLayout(layout)
        return self.widget
    
    def get_candidate_dialog(self, candidate):
        if candidate.id not in self.candidate_dialogs:
            self.candidate_dialogs[candidate.id] = CandidateDetailsDialog(candidate, self)
        return self.candidate_dialogs[candidate.id]

    def display_candidate_details(self, item):
        candidate = item.data(Qt.UserRole)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        dialog = self.get_candidate_dialog(candidate)
        if not dialog:
            dialog = CandidateDetailsDialog(candidate, self)
            self.candidate_dialogs[candidate.id] = dialog

        dialog.exec_()

    def match_candidates(self):
        self.matchCandidatesButton.setEnabled(False)
        self.matchCandidatesButton.setText("Matching Candidates...")
        self.matchingWorker = MatchingWorker(self.agent, self.par.all_profiles, [self.job])
        self.matchingWorker.profiles_found.connect(self.par.populate_candidates_tab)
        self.matchingWorker.completed.connect(self.on_match_complete)
        self.matchingWorker.error.connect(self.show_error)
        self.matchingWorker.start()

    def on_match_complete(self, message):
        self.matchCandidatesButton.setText("Match Candidates")
        self.matchCandidatesButton.setEnabled(True)
        QMessageBox.information(self, "Matching Complete", message)

    def show_error(self, message):
        self.matchCandidatesButton.setText("Match Candidates")
        self.matchCandidatesButton.setEnabled(True)
        QMessageBox.information(self, "Error", message)

    def create_motivations(self):
        self.createMotivationButton.setEnabled(False)
        self.createMotivationButton.setText("Creating Motivation Letters...")
        candidates = [self.candidateList.item(i).data(Qt.UserRole) for i in range(self.candidateList.count())
                        if self.candidateList.item(i).checkState() == Qt.Checked]
        
        self.motivationWorker = MotivationWorker(self.agent, self.job, candidates)
        self.motivationWorker.completed.connect(self.on_motivation_completed)
        self.motivationWorker.error.connect(self.on_motivation_error)
        self.motivationWorker.start()

    def on_motivation_completed(self, message):
        candidates = [self.candidateList.item(i).data(Qt.UserRole) for i in range(self.candidateList.count())]
        # self.populate_motivations_tab(candidates)
        for candidate in candidates:
            dialog = self.get_candidate_dialog(candidate)
            if dialog:
                dialog.motivationWidget.setText(candidate.get_job_match(self._id)[1])

        self.createMotivationButton.setText("Recreate Motivation Letters")
        self.createMotivationButton.setEnabled(True)
        QMessageBox.information(self, "Success", message)

    def on_motivation_error(self, message):
        self.createMotivationButton.setText("Create Motivation Letter")
        self.createMotivationButton.setEnabled(True)
        QMessageBox.information(self, "Error", message)

    def load_matched_candidates(self):
        matched_candidates = self.matchdao.get_candidates_for_job(self.job.id)
        print("Matched Candidates:", matched_candidates)  # Debugging line
        self.populate_candidates_tab(matched_candidates)

    def populate_candidates_tab(self, candidates):
        self.candidateList.clear()  # Clear existing entries
        for candidate in candidates:
            if candidate is not None:
                item = QListWidgetItem(candidate.name)
                item.setData(Qt.UserRole, candidate)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item.setCheckState(Qt.Unchecked)
                self.candidateList.addItem(item)
            else:
                # Log or handle the case where candidate is None
                print("Encountered None candidate, skipping...")

class CandidateDetailsDialog(QDialog):
    def __init__(self, candidate, parent: JobDetailsDialog):
        super().__init__()
        self.candidate = candidate
        self._id = candidate.id
        self._parent = parent
        self._parent_id = parent.id
        self.initUI()

    @property
    def id(self):
        return self._id
    
    @property
    def parent(self):
        return self._parent
    
    @property
    def parent_id(self):
        return self._parent_id

    def initUI(self):
        self.setWindowTitle("Candidate Details")
        self.setGeometry(100, 100, 600, 400)
        self.setMaximumWidth(800)  # Set initial size and position

        layout = QVBoxLayout()

        widget = QTabWidget()
        widget.addTab(self.create_candidate_tab(), "Candidate")
        widget.addTab(self.create_motivation_tab(self._parent_id), "Motivation")

        layout.addWidget(widget)

        self.setLayout(layout)
    
    def create_candidate_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Name: {self.candidate.name}"))
        return widget

    def create_motivation_tab(self, parent_id):
        widget = QWidget()
        layout = QVBoxLayout()
        self.motivationWidget = QTextBrowser()
        if isinstance(self.candidate, Profile):
            self.motivationWidget.setText(self.candidate.get_job_match(parent_id)[1])
        elif isinstance(self.candidate, CandidateModel):
            self.motivationWidget.setText(self._parent.matchdao.get_motivation(self._parent.job.id, self.candidate.id))
        layout.addWidget(self.motivationWidget)

        self.createMotivationButton = QPushButton("Create Motivation Letter")
        self.createMotivationButton.clicked.connect(self.create_motivation)
        layout.addWidget(self.createMotivationButton)

        widget.setLayout(layout)
        return widget
    
    def create_motivation(self):
        self.createMotivationButton.setEnabled(False)
        self.createMotivationButton.setText("Creating Motivation Letter...")
        candidates = [self.candidate]
        
        self.motivationWorker = MotivationWorker(self.parent.agent, self.parent.job, candidates)
        self.motivationWorker.completed.connect(self.on_motivation_completed)
        self.motivationWorker.error.connect(self.on_motivation_error)
        self.motivationWorker.start()

    def on_motivation_completed(self, message):
        motivation = self.candidate.get_job_match(self.parent_id)[1]
        self.motivationWidget.setText(motivation)
        QMessageBox.information(self, "Success", message)
        self.createMotivationButton.setText("Recreate Motivation Letter")
        self.createMotivationButton.setEnabled(True)

    def on_motivation_error(self, message):
        QMessageBox.information(self, "Error", message)

