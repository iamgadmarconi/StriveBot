import requests

from bs4 import BeautifulSoup

from src.utils import (
    Agent,
    clean_text,
    categorize_description,
    get_parameters_from_raw_description,
)


class Assignment:
    def __init__(self, description: dict) -> None:
        self._description = description
        self._skills = self._description.get("SKILLS")
        self._requirements = self._description.get("REQUIREMENTS")
        self._preferences = self._description.get("PREFERENCES")

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

        self._soup = self._get_soup()

        self._commitment = None
        self._start = None
        self._location = None
        self._max_hourly_rate = None
        self._end = None
        self._deadline = None
        self._submitter = None

        self._status = self._get_job_status()
        self._candidates = []
        self._get_job_params()
        self._assignment = self._get_assignment_from_url()

    @property
    def soup(self):
        return self._soup

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
    def location(self):
        return self._location

    @property
    def max_hourly_rate(self):
        return self._max_hourly_rate

    @property
    def end(self):
        return self._end

    @property
    def deadline(self):
        return self._deadline

    @property
    def submitter(self):
        return self._submitter

    @property
    def status(self):
        return self._status

    @property
    def candidates(self):
        return self._candidates

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

    @location.setter
    def location(self, value):
        self._location = value

    @max_hourly_rate.setter
    def max_hourly_rate(self, value):
        self._max_hourly_rate = value

    @end.setter
    def end(self, value):
        self._end = value

    @deadline.setter
    def deadline(self, value):
        self._deadline = value

    @submitter.setter
    def submitter(self, value):
        self._submitter = value

    @candidates.setter
    def candidates(self, value: tuple):
        self._candidates.append(value)

    @assignment.setter
    def assignment(self, value: Assignment):
        self._assignment = value

    @status.setter
    def status(self, value):
        self._status = value

    def __repr__(self) -> str:
        return f"Job({self.position}, {self.company}, {self.description}, {self.skills}, {self.commitment}, {self.location}, {self.start})"

    def __str__(self) -> str:
        return f"""
                Job Details
                ------------
                Company: {self.company}

                Position: {self.position}

                Assignment:
                ------------
                {self.assignment}
                """

    def _get_soup(self) -> BeautifulSoup:
        html_file = requests.get(self.url).text
        soup = BeautifulSoup(html_file, "html.parser")
        return soup

    def _get_job_status(self) -> str:
        print(f"\nGetting job status for:\n{self.position} at {self.company}\n")

        button_div = self.soup.find(
            "div",
            class_="hfp_button hfp-button-outline-success no-transition mb-4 d-none d-sm-block",
        )

        # Find the <a> tag within that div
        try:
            a_tag = button_div.find("a")
        except AttributeError:
            a_tag = None

        # Extract and return the text, if the <a> tag is found
        return a_tag.text.strip() if a_tag else None

    def _get_raw_job_description(self) -> str:
        print(f"\nGetting job description for:\n{self.position} at {self.company}\n")

        assignments = self.soup.find("div", {"id": "hfp_assignments"})
        description = assignments.find("div", class_="hfp_content").text.strip()
        # print(f"\n --debug--\n\nDescription: {description}\n--debug--\n")
        cleaned_text = clean_text(description)
        return cleaned_text

    def _get_raw_job_params(self) -> str:
        print(f"\nGetting raw job parameters for:\n{self.position} at {self.company}\n")

        info_block = self.soup.find("div", {"id": "hfp_assignment-info-block"})

        # Find all 'hfp_item' divs within the 'hfp_assignment_info_block'
        hfp_items = info_block.find_all("div", class_="hfp_item")

        params_info = {}

        for item in hfp_items:
            # The key is the text of the 'p' tag
            key = item.find("p").text.strip().lower() if item.find("p") else None
            # The value is the text of the 'b' tag
            value = item.find("b").text.strip() if item.find("b") else None

            # If a key is found, add the key-value pair to the assignment_info dictionary
            if key:
                params_info[key] = value

        return "\n".join(
            f"{key.capitalize()}: {value}" for key, value in params_info.items()
        )

    def _get_assignment_from_url(self) -> Assignment:
        print(f"\nGetting assignment for:\n{self.position} at {self.company}\n")
        # print(f"\nCleaned text:\n {cleaned_text}\n")
        cleaned_text = self._get_raw_job_description()
        assignment = Assignment(categorize_description(self.agent, cleaned_text))
        return assignment

    def _get_job_params(self) -> dict:
        print(f"\nGetting job parameters for:\n{self.position} at {self.company}\n")
        cleaned_text = self._get_raw_job_params() + self._get_raw_job_description()
        params = get_parameters_from_raw_description(self.agent, cleaned_text)

        key_to_attribute = {
            "commitment": "commitment",
            "location": "location",
            "max_hourly_rate": "max_hourly_rate",
            "end_date": "end",
            "deadline": "deadline",
            "submitter": "submitter",
        }

        for key, value in params.items():
            attr = key_to_attribute.get(key)
            if attr and hasattr(self, attr):
                setattr(self, attr, value)


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
