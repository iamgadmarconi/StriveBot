import re
import traceback

from PyQt5.QtCore import QThread, pyqtSignal
from threading import Event


from src.scraper import get_jobs, Job
from src.agent import get_profiles_from_match


class Worker(QThread):
    finished = pyqtSignal(list)
    update_status = pyqtSignal(str, object)
    paused = pyqtSignal(bool)
    canceled = pyqtSignal()  # Define the canceled signal

    def __init__(self, agent, input_text, all_profiles):
        super().__init__()
        self.agent = agent
        self.input_text = input_text
        self.all_profiles = all_profiles
        self._is_running = True
        self._pause_event = Event()
        self._pause_event.set()  # Start unpaused

    def run(self):
        if re.match(r'https?://', self.input_text):
            # Input is a URL, process as a single job directly
            job = Job(self.agent, url=self.input_text)  # Assuming the Job constructor can handle URL directly
            self.update_status.emit(f'Found: {job.position} at {job.company}', job)
            self.finished.emit([job])  # Emit the single job in a list

        else:
            # Process as a search term through get_jobs
            jobs_generator = get_jobs(self.agent, self.input_text)
            for job in jobs_generator:
                self._pause_event.wait()
                if not self._is_running:
                    self.canceled.emit()
                    return

                self.update_status.emit(f'Found: {job.position} at {job.company}', job)

            if self._is_running:
                self.finished.emit([])  # Emit empty list if running but no specific job handling required


    def pause(self):
        self._pause_event.clear()
        self.paused.emit(True)

    def resume(self):
        self._pause_event.set()
        self.paused.emit(False)

    def stop(self):
        self._is_running = False
        self.resume()  # Resume to allow the thread to exit

class MatchingWorker(QThread):
    profiles_found = pyqtSignal(list, object)
    error = pyqtSignal(str)

    def __init__(self, agent, profiles, jobs):
        super().__init__()
        self.agent = agent
        self.profiles = profiles
        self.jobs = jobs

    def run(self):
        try:
            for job in self.jobs:
                print(f"Matching for {job.position} at {job.company}")
                candidates = get_profiles_from_match(self.agent, self.profiles, job)
                self.profiles_found.emit(candidates, job)
                print(f"Found {len(candidates)} candidates for {job.position} at {job.company}")
        except Exception as e:
            self.error.emit(str(e))