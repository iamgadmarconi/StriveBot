from dotenv import load_dotenv

from src.profiles import ProfileManager
from src.scraper import get_jobs, Job
from src.utils import Agent
from src.agent import motivation_letter, profile_matcher, profile_from_names

load_dotenv()


def main():
    agent = Agent()

    profiles = ProfileManager()

    sample_job_1 = Job(
        agent,
        "https://striive.com/nl/opdrachten/ministerie-van-economische-zaken-en-klimaat-dictu/senior-citrix-beheerder/ae1b2b31-a4ca-4cd9-8e46-c494a725ac50",
        "Senior Citrix Administrator",
        "Ministry of Economic Affairs and Climate Policy (DICTU)",
    )

    sample_job_2 = Job(
        agent,
        "https://striive.com/nl/opdrachten/ministerie-van-justitie-veiligheid-jenv/software-engineer/73d85ece-68cc-42d3-bb58-924354fd9d5e",
        "Software Engineer",
        "Ministry of Justice and Security (JenV)",
    )

    # jobs = get_jobs(agent)
    sample_jobs = [sample_job_1, sample_job_2] # for testing

    matches = []

    for job in sample_jobs:
        profiles = profile_matcher(agent, profiles, job)
        if profiles:
            profiles = profile_from_names(profiles)
            for profile in profiles:
                print(f"\nProfile matched for {job.position} at {job.company}:\n{profile}\n")
                data = {
                    "Position": job.position,
                    "Company": job.company,
                    "Candidate": profile,
                    "Motivation": motivation_letter(agent, profile, job),
                }

                matches.append(data)

    return matches


if __name__ == "__main__":
    main()
