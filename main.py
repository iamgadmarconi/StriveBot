from dotenv import load_dotenv

from src.profiles import ProfileManager
from src.scraper import get_jobs
from src.utils import Agent
from src.agent import motivation_letter, profile_matcher

load_dotenv()


def main():
    agent = Agent()

    profiles = ProfileManager()

    # sample_job = Job(
    #     agent,
    #     "https://striive.com/nl/opdrachten/ministerie-van-economische-zaken-en-klimaat-dictu/senior-citrix-beheerder/ae1b2b31-a4ca-4cd9-8e46-c494a725ac50",
    #     "Senior Citrix Administrator",
    #     "Ministry of Economic Affairs and Climate Policy (DICTU)",
    # )

    jobs = get_jobs(agent)

    matches = []

    for job in jobs:
        profile = profile_matcher(agent, profiles, job)
        if profile:

            data = {
                "Position": job.position,
                "Company": job.company,
                "Candidate": profile,
                "Motivation": motivation_letter(agent, profile, job),
            }

        matches.append(data)


if __name__ == "__main__":
    main()
