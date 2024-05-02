import os

import pandas as pd

from src.utils import get_id_from_name, get_base_path


class Motivation:
    def __init__(self, job, motivation: str) -> None:
        self._job = job
        self._motivation = motivation
        self._id = get_id_from_name(motivation[30:50])

    @property
    def id(self) -> str:
        return self._id
    
    @property
    def job(self) -> str:
        return self._job
    
    @property
    def motivation(self) -> str:
        return self._motivation
    
    @motivation.setter
    def motivation(self, new_motivation: str):
        self._motivation = new_motivation

    def __repr__(self) -> str:
        return f"Motivation(Job ID: {self.job_id}, Motivation: {self.motivation})"
    
    def __str__(self) -> str:
        return self.motivation

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
        self._id = get_id_from_name(self.name)

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
    
    def add_job_match(self, motivation: Motivation) -> None:
        self._job_matches.append((motivation.job, motivation.motivation))

    def get_job_match(self, job_id) -> tuple[object, str]:
        for j, m in self._job_matches:
            if j.id == job_id:
                return j, m
        return None

    def update_motivation(self, new_motivation: Motivation) -> None:
            # Update motivation in the Candidate's job_matches list
            for index, (j, m) in enumerate(self.job_matches):
                if j.id == new_motivation.job.id:
                    self.job_matches[index] = (j, new_motivation.motivation)  # Update the tuple in the list
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


def get_data() -> dict:
    file_path = os.path.join(get_base_path(), r'candidates\candidates.csv')
    if not os.path.exists(file_path):
        raise "No candidate file"
    df = pd.read_csv(file_path, delimiter=";")
    return df.to_dict(orient="records")


def create_profile_from_candidate(candidate_model):
    # Retrieve the candidate from the database
    candidate = candidate_model

    # Create a dictionary from the CandidateModel data
    candidate_data = {
        "name": candidate.name,
        "interests": candidate.interests,
        "experience": candidate.experience,
        "skills": candidate.skills,
        "education": candidate.education,
        "profile": candidate.profile,
        "certifications": candidate.certificates,
        "id": candidate.id,
    }

    profile = Profile(candidate_data)
    return profile