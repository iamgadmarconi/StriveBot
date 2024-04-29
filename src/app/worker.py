from PyQt5.QtCore import QThread, pyqtSignal


from src.scraper import get_jobs, Job


class Worker(QThread):
    finished = pyqtSignal(list)
    update_status = pyqtSignal(str, Job)
    canceled = pyqtSignal()

    def __init__(self, agent, input_text, all_profiles):
        super().__init__()
        self.agent = agent
        self.input_text = input_text
        self.all_profiles = all_profiles
        self._is_running = True  # Initialize _is_running here

    def run(self):
        matches = []

        jobs_generator = get_jobs(self.agent, self.input_text)
        for job in jobs_generator:
            if not self._is_running:
                self.canceled.emit()
                break
            self.update_status.emit(f"Processing: {job.position} at {job.company}", job)

        if self._is_running:
            self.finished.emit(matches)

    def stop(self):
        self._is_running = False  # Method to stop the thread
