import pandas as pd


class Profile:

    def __init__(self, data) -> None:
        self.name = data["name"]
        self.profile = data["profile"]
        self.experience = data["experience"]
        self.skills = data["skills"]

    def __repr__(self) -> str:
        return f"Profile(Name: {self.name}, Profile: {self.profile}, Skills: {self.skills}, Experience: {self.experience})"


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

    def get_profiles_description(self) -> str:
        description = ""
        for profile in self.profiles:
            description += "\n--------------------------------------------------\n"
            description += f"**Name**: {profile.name}\n"
            description += f"**Profile**: {profile.profile}\n"
            description += f"**Experience**: {profile.experience}\n"
            description += f"**Skills**: {profile.skills}\n"

        return description


def get_data(file_name: str = r"src\candidates\candidates.csv") -> dict:
    df = pd.read_csv(file_name, delimiter=";")
    return df.to_dict(orient="records")

