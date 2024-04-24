from dotenv import load_dotenv

from src.profiles import ProfileManager
from src.scraper import get_jobs, Job
from src.utils import Agent

load_dotenv()


def main():
    agent = Agent()

    profiles = ProfileManager()

    sample_job = Job(
        agent,
        "https://striive.com/nl/opdrachten/ministerie-van-economische-zaken-en-klimaat-dictu/senior-citrix-beheerder/ae1b2b31-a4ca-4cd9-8e46-c494a725ac50",
        "Senior Citrix Administrator",
        "Ministry of Economic Affairs and Climate Policy (DICTU)",
    )

    print(sample_job.assignment.skills, sample_job.assignment.requirements, sample_job.assignment.preferences)


if __name__ == "__main__":
    main()
