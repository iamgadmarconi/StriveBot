import requests
import hashlib

from bs4 import BeautifulSoup

from src.utils import (
    Agent,
    clean_text,
    categorize_description,
    get_parameters_from_raw_description,
)


class Contact:
    def __init__(self, name: str, phone: str = None, email: str = None) -> None:
        self._name = name
        self._phone = phone
        self._email = email

    @property
    def name(self):
        return self._name
    
    @property
    def phone(self):
        return self._phone
    
    @property
    def email(self):
        return self._email
    
    @name.setter
    def name(self, value):
        self._name = value

    @phone.setter
    def phone(self, value):
        self._phone = value

    @email.setter
    def email(self, value):
        self._email = value

    def __repr__(self) -> str:
        return f"Contact({self.name}, {self.phone}, {self.email})"
    
    def __str__(self) -> str:
        return f"""
                Contact Information
                -------------------
                Name: {self.name}
                Phone: {self.phone}
                Email: {self.email}
        """


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
    def __init__(self, agent: Agent, url: str, position: str=None, company: str=None) -> None:
        self._agent = agent
        self._url = url
        self._soup = self._get_soup()

        self.position = position
        self.company = company
        self._commitment = None
        self._start = None
        self._location = None
        self._max_hourly_rate = None
        self._end = None
        self._deadline = None

        self._check_complete()
        self._status = self._get_job_status()
        self._submitter = self._get_job_submitter()
        self._candidates = []
        self._get_job_params()
        self._assignment = self._get_assignment_from_url()

        m = hashlib.md5()
        m.update(f"{self.position}{self.company}".encode())
        self._id = str(int(m.hexdigest(), 16))[0:12]

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
    
    @property
    def id(self):
        return self._id

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
    def submitter(self, value: Contact):
        self._submitter = value

    @candidates.setter
    def candidates(self, value):
        self._candidates.append(value)

    @assignment.setter
    def assignment(self, value: Assignment):
        self._assignment = value

    @status.setter
    def status(self, value):
        self._status = value

    def update_motivation(self, candidate, motivation):
        if c.id in [c.id for c in self.candidates]:
            for c, m in self.candidates:
                if c.id == candidate.id:
                    c.update_motivation(motivation)
                    break

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
    
    def _check_complete(self) -> None:
        if not self.position or not self.company:
            details = self._force_complete()
            self.position = details['position']
            self.company = details['company']
            
    def _force_complete(self) -> dict[str, str]:
        details = {}
        container = self.soup.find('div', class_='hfp_url-segments')
        spans = container.find_all('span')

        details['company'] = spans[0].get_text(strip=True) if spans else None
        details['position'] = spans[1].get_text(strip=True) if len(spans) > 1 else None

        return details

    def _get_job_status(self) -> str:
        # print(f"\nGetting job status for:\n{self.position} at {self.company}\n")

        button_div = self.soup.find(
            "div",
            class_="hfp_button hfp-button-outline-success no-transition mb-4 d-none d-sm-block",
        )

        try:
            a_tag = button_div.find("a")
        except AttributeError:
            a_tag = None

        return a_tag.text.strip() if a_tag else None
    
    def _get_job_submitter(self) -> Contact:
        # print(f"\nGetting job submitter for:\n{self.position} at {self.company}\n")

        submitter_block = self.soup.find("div", {"id": "hfp_recruiter-info-block"})

        name_tag = submitter_block.find("b")
        name = name_tag.get_text(strip=True) if name_tag else None

        contact_div = submitter_block.find('div', class_='d-none d-sm-block hfp_ellipsize')

        # Extract the email address
        email_address = contact_div.a.get_text(strip=True)

        # Extract the phone number
        phone_number = contact_div.p.get_text(strip=True)

        # print(f"\n\nName: {name}\nEmail: {email_address}\nPhone: {phone_number}\n\n")

        return Contact(name, phone_number, email_address)

    def _get_raw_job_description(self) -> str:
        # print(f"\nGetting job description for:\n{self.position} at {self.company}\n")

        assignments = self.soup.find("div", {"id": "hfp_assignments"})
        description = assignments.find("div", class_="hfp_content").text.strip()
        # print(f"\n --debug--\n\nDescription: {description}\n--debug--\n")
        cleaned_text = clean_text(description)
        return cleaned_text

    def _get_raw_job_params(self) -> str:
        info_block = self.soup.find("div", {"id": "hfp_assignment-info-block"})

        hfp_items = info_block.find_all("div", class_="hfp_item")

        params_info = {}

        for item in hfp_items:
            # The key is the text of the 'p' tag
            key = item.find("p").text.strip().lower() if item.find("p") else None
            # The value is the text of the 'b' tag
            value = item.find("b").text.strip() if item.find("b") else None

            if key:
                params_info[key] = value

        # print("\n".join(
        #     f"{key.capitalize()}: {value}" for key, value in params_info.items()
        # ))

        return "\n".join(
            f"{key.capitalize()}: {value}" for key, value in params_info.items()
        )

    def _get_assignment_from_url(self) -> Assignment:
        # print(f"\nGetting assignment for:\n{self.position} at {self.company}\n")
        # print(f"\nCleaned text:\n {cleaned_text}\n")
        cleaned_text = self._get_raw_job_description()
        assignment = Assignment(categorize_description(self.agent, cleaned_text))
        return assignment

    def _get_job_params(self) -> dict:
        # print(f"\nGetting job parameters for:\n{self.position} at {self.company}\n")
        cleaned_text = self._get_raw_job_params() + self._get_raw_job_description()
        params = get_parameters_from_raw_description(self.agent, cleaned_text)

        key_to_attribute = {
            "commitment": "commitment",
            "location": "location",
            "max_hourly_rate": "max_hourly_rate",
            "start_date": "start",
            "end_date": "end",
            "deadline": "deadline",
        }

        for key, value in params.items():
            attr = key_to_attribute.get(key)
            if attr and hasattr(self, attr):
                setattr(self, attr, value)


def get_jobs(agent: Agent, query: str = None):
    url = (
        f"https://striive.com/nl/opdrachten/?query={query}"
        if query
        else "https://striive.com/nl/opdrachten/"
    )

    html_file = requests.get(url).text
    soup = BeautifulSoup(html_file, "html.parser")
    job_cards = soup.find_all("div", class_="col-md-4")

    for card in job_cards:
        link = card.find("a", href=True)["href"] if card.find("a", href=True) else None
        title = card.find("div", class_="hfp_card-title hfp_ellipsize").text.strip() if card.find("div", class_="hfp_card-title hfp_ellipsize") else "No Title"
        company = card.find("div", class_="hfp_card-company hfp_ellipsize").text.strip() if card.find("div", class_="hfp_card-company hfp_ellipsize") else "No Company"

        job = Job(agent, link, title, company)

        yield job

def collect_all_jobs(agent: Agent, query=None) -> list[Job]:
    all_jobs = []
    for job in get_jobs(agent, query):
        all_jobs.append(job)
    return all_jobs
