import hashlib
import pandas as pd

class Profile:

    def __init__(self, data) -> None:
        self.name = data["name"]
        self.interests = data["interests"]
        self.experience = data["experience"]
        self.skills = data["skills"]
        self.education = data["education"]
        self.profile = data["profile"]
        self.certificates = data["certifications"]
        self._job_matches = []

        m = hashlib.md5()
        m.update(self.name.encode())
        self._id = str(int(m.hexdigest(), 16))[0:12]

    @property
    def id(self) -> str:
        return self._id
    
    @property
    def job_matches(self) -> list:
        return self._job_matches

    def __repr__(self) -> str:
        return f"Profile(Name: {self.name}, Profile: {self.interests}, Skills: {self.skills}, Experience: {self.experience}, Education: {self.education})"

    def __str__(self) -> str:
        return f"""
                -------------------
                Profile Details for {self.name}
                Skills: {self.skills}
                Experience: {self.experience}
                Interests: {self.interests}
                Education: {self.education}
                Profile: {self.profile}
                Certificates: {self.certificates}
                """
    
    def add_job_match(self, job, motivation: str) -> None:
        self._job_matches.append((job, motivation))

    @job_matches.getter
    def get_job_match(self, job_id) -> tuple:
        for j, m in self._job_matches:
            if j.id == job_id:
                return j, m
        return None

    def update_motivation(self, job, motivation: str) -> None:
        if job.id in [j.id for j, _ in self._job_matches]:
            for j, m in self._job_matches:
                if j.id == job.id:
                    j.update_motivation(motivation)
                    break


class ProfileManager:

    def __init__(self) -> None:
        self.profiles = []
        self.load_profiles()

    def load_profiles(self) -> list:
        for data in get_data():
            self.add_profile(Profile(data))

    def add_profile(self, profile: Profile):
        self.profiles.append(profile)

    def get_profile(self, name: str) -> Profile:
        for profile in self.profiles:
            if profile.name == name:
                return profile
        return None

    def __repr__(self) -> str:
        return f"ProfileManager(Profiles: {self.profiles})"
    
    def __str__(self) -> str:
        return self.get_profiles_description()

    def get_profiles_description(self) -> str:
        description = ""
        for profile in self.profiles:
            description += str(profile) + "\n"

        return description


def get_data(file_name: str = r"src\candidates\candidates.csv") -> dict:
    df = pd.read_csv(file_name, delimiter=";")
    return df.to_dict(orient="records")
