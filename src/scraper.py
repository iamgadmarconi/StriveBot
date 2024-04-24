import requests

from bs4 import BeautifulSoup

from src.utils import clean_text, Agent, categorize_description


class Assignment:
    def __init__(self, description: dict) -> None:
        self._description = description
        self._skills = self._description.get("SKILLS")
        self._requirements = self._description.get("REQUIREMENTS")
        self._preferences = self._description.get("PREFERENCES")
        self._location = None

    @property
    def description(self):
        return self._description

    @property
    def skills(self):
        return self._skills

    @property
    def requirements(self):
        return self._requirements

    @property
    def preferences(self):
        return self._preferences

    @property
    def location(self):
        return self._location

    @description.setter
    def description(self, value):
        self._description = value

    @skills.setter
    def skills(self, value):
        self._skills = value

    @requirements.setter
    def requirements(self, value):
        self._requirements = value

    @preferences.setter
    def preferences(self, value):
        self._preferences = value

    @location.setter
    def location(self, value):
        self._location = value

    def __repr__(self) -> str:
        return f"Assignment({self.preferences}, {self.requirements}, {self.skills}"

    def __str__(self) -> str:
        return f"""Assignment Details
                -------------------
                Requirements: {self.requirements}

                Preferences: {self.preferences}

                Skills: {self.skills}
        """


class Job:
    def __init__(self, agent: Agent, url: str, position: str, company: str) -> None:
        self._agent = agent
        self._url = url
        self.position = position
        self.company = company
        self._commitment = None
        self._start = None
        self._assignment = self._get_assignment_from_url()

    @property
    def agent(self):
        return self._agent

    @property
    def url(self):
        return self._url

    @property
    def commitment(self):
        return self._commitment

    @property
    def start(self):
        return self._start

    @property
    def assignment(self):
        return self._assignment

    @url.setter
    def url(self, value):
        self._url = value

    @commitment.setter
    def commitment(self, value):
        self._commitment = value

    @start.setter
    def start(self, value):
        self._start = value

    @assignment.setter
    def assignment(self, value):
        self._assignment = value

    def __repr__(self) -> str:
        return f"Job({self.position}, {self.company}, {self.description}, {self.skills}, {self.commitment}, {self.location}, {self.start})"

    def __str__(self) -> str:
        return f"""
                Job Details
                ------------
                Company: {self.company}

                Position: {self.position}

                Commitment: {self.commitment}

                Start: {self.start}

                Assignment:
                ------------
                {self.assignment}

                URL: {self.url}
                """

    def _get_assignment_from_url(self) -> Assignment:
        html_file = requests.get(self.url).text
        soup = BeautifulSoup(html_file, "html.parser")
        assignments = soup.find("div", {"id": "hfp_assignments"})
        description = assignments.find("div", class_="hfp_content").text.strip()

        self.assignment = Assignment(categorize_description(self.agent, clean_text(description)))


def get_jobs(agent, query: str = None) -> list[Job]:
    url = (
        f"https://striive.com/nl/opdrachten/?query={query}"
        if query
        else "https://striive.com/nl/opdrachten/"
    )

    html_file = requests.get(url).text

    soup = BeautifulSoup(html_file, "html.parser")

    job_cards = soup.find_all("div", class_="col-md-4")

    jobs = []

    for card in job_cards:
        link = card.find("a", href=True)["href"] if card.find("a", href=True) else None
        title = card.find("div", class_="hfp_card-title hfp_ellipsize").text.strip()
        company = card.find("div", class_="hfp_card-company hfp_ellipsize").text.strip()

        icon_blocks = card.find_all("div", class_="hfp_card-icons-block-item")

        # Assuming the first block item is hours per week and the second is the date
        commitment = icon_blocks[0].text.strip() if icon_blocks else None
        start = icon_blocks[1].text.strip() if len(icon_blocks) > 1 else None

        job = Job(agent, link, title, company)
        job.commitment = commitment
        job.start = start

        jobs.append(job)

    return jobs
