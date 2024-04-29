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
)
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices, QColor, QIcon
from PyQt5.QtCore import QUrl

from src.utils import format_bulleted_list


class JobDetailsDialog(QDialog):
    def __init__(self, job):
        super().__init__()
        self.job = job
        self._id = job.id
        self.initUI()

    @property
    def id(self):
        return self._id

    def initUI(self):
        self.setWindowTitle("Job Details")
        self.setGeometry(100, 100, 600, 400) 
        self.setMaximumWidth(800) # Set initial size and position

        layout = QVBoxLayout(self)

        # Create the tab widget
        tabWidget = QTabWidget()
        tabWidget.addTab(self.create_main_tab(), "Main")
        tabWidget.addTab(self.create_calendar_tab(), "Calendar")
        tabWidget.addTab(self.create_contact_tab(), "Contact")
        tabWidget.addTab(self.create_assignment_tab(), "Assignment")
        tabWidget.addTab(self.create_candidates_tab(), "Candidates")

        layout.addWidget(tabWidget)

    def create_text_display_widget(self, text, bulleted=False):
        """ Helper to create a text display widget that handles text wrapping. """
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
        if self.job._status == "Open":
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
        if self.job._submitter:
            grid.addWidget(QLabel("Name:"), 0, 0)
            grid.addWidget(QLabel(self.job.submitter.name), 0, 1)
            grid.addWidget(QLabel("Email:"), 1, 0)
            grid.addWidget(QLabel(self.job.submitter.email), 1, 1)
            grid.addWidget(QLabel("Phone:"), 2, 0)
            grid.addWidget(QLabel(self.job.submitter.phone), 2, 1)
        widget.setLayout(grid)
        return widget

    def create_assignment_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        if self.job.assignment:

            layout.addWidget(QLabel('Requirements:'))
            requirementsWidget = self.create_text_display_widget(self.job.assignment.requirements, bulleted=True)
            layout.addWidget(requirementsWidget)

            layout.addWidget(QLabel('Skills:'))
            skillsWidget = self.create_text_display_widget(self.job.assignment.skills, bulleted=True)
            layout.addWidget(skillsWidget)

            layout.addWidget(QLabel('Preferences:'))
            preferencesWidget = self.create_text_display_widget(self.job.assignment.preferences, bulleted=True)
            layout.addWidget(preferencesWidget)
        widget.setLayout(layout)
        return widget


    def create_candidates_tab(self):
        self.widget = QWidget()
        layout = QVBoxLayout()
        self.candidateList = QListWidget()
        
        self.candidateList.itemClicked.connect(self.display_candidate_details)

        # Wrap the candidate list in a scroll area
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(self.candidateList)
        layout.addWidget(scrollArea)
        self.widget.setLayout(layout)
        return self.widget

    def display_candidate_details(self, item):
        candidate = item.data(Qt.UserRole)
        # Display candidate details in a new dialog or update a section in this dialog
        QMessageBox.information(
            self, "Candidate Details", f"Name: {candidate.name}\nMore info..."
        )
