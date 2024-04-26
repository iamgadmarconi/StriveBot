from dotenv import load_dotenv

from src.profiles import ProfileManager
from src.utils import Agent, pretty_print_matches
from src.scraper import Job, get_jobs
from src.agent import motivation_letter, profile_matcher, profile_from_names
from src.save import save_job_to_csv

load_dotenv()


def main(debug=True):
    agent = Agent()

    all_profiles = ProfileManager()

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

    if not debug:
        jobs = get_jobs(agent)

    jobs = [sample_job_1, sample_job_2]  # for testing

    matches = []

    for job in jobs:
        # print(job)
        profiles = profile_matcher(agent, all_profiles, job)
        if profiles:
            profile_obj = profile_from_names(profiles)
            for profile in profile_obj:
                print(
                    f"\nProfile matched for {job.position} at {job.company}:\n{profile}\n"
                )
                motivation = motivation_letter(agent, profile, job)
                job.candidates = (profile, motivation)
                profile.add_job_match(job, motivation)
                data = {
                    "Position": job.position,
                    "Company": job.company,
                    "Candidate": profile,
                    "Motivation": motivation,
                }
                pretty_print_matches(data)

                matches.append(data)

            save_job_to_csv(job, force=True)

    return matches


if __name__ == "__main__":
    main()
