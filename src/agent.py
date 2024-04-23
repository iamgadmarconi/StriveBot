import os

from openai import OpenAI

from src.profiles import Profile, ProfileManager
from src.scraper import Job


class Agent:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)

    def motivation_letter(self, profile: Profile, job: Job):
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": 
                        f"""
                        INCLUDE THE FOLLOWING HEADER IN YOUR MOTIVATION LETTER:\n
                        'Subject: Application for the position of {job.position}'\n
                        'Address: MareVisie B.v., Delft, Netherlands'\n

                        You are an assistant helping a candidate write a motivation letter for a job application.
                        The candidate is applying to the following position:\n
                        {job.position}.\n

                        The job has the following description:\n
                        {job.description}\n

                        The job requires the following skills:\n
                        {job.skills}\n

                        The candidate, {profile.name}, has the following profile:\n
                        {profile.profile}\n

                        The candidate has the following experience:\n
                        {profile.experience}\n

                        The candidate has the following skills:\n
                        {profile.skills}\n
                        """
                },
                {
                    "role": "user", 
                    "content": "Write a motivation letter for the candidate in first person. The tone should be formal and professional Be concise."
                },
            ],
            temperature=0.1,
        )

        return response.choices[0].message.content


    def profile_matcher(self,  profiles: ProfileManager, job: Job) -> Profile:

        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": 
                        f"""
                        BE EXTREMELY CRITICAL IN YOUR SELECTION. ONLY MATCH CANDIDATES IF THEY HAVE THE REQUIRED SKILLS.\n

                        RETURN **ONLY** THE NAME OF THE BEST MATCHING CANDIDATES (UP TO A MAXIMUM OF 3) FOR THE JOB.\n

                        You are an assistant designed to match job openings to potential candidates.
                        The job is the following:\n
                        {job.position}.\n

                        The job has the following description:\n
                        {job.description}\n

                        The job requires the following skills:\n
                        {job.skills}\n

                        You have the following candidates:\n
                        {profiles.get_profiles_description()}\n
                        """
                },
                {
                    "role": "user", 
                    "content": "Return the name of the best matching candidates (up to a maximum of 3) for the job. Be critical in your selection."
                },
            ],
            temperature=0.1,
        )

        return response.choices[0].message.content