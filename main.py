from dotenv import load_dotenv

from src.profiles import ProfileManager
from src.scraper import get_jobs
from src.utils import Agent

load_dotenv()

def main():
    agent = Agent()


    profiles = ProfileManager()
    jobs = get_jobs(agent)

    for job in jobs:
        print(job)


if __name__ == "__main__":
    main()