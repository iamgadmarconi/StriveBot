from src.profiles import Profile, ProfileManager, Motivation
from src.scraper import Job
from src.utils import Agent


def motivation_letter(agent: Agent, profile: Profile, job: Job):
    response = agent.client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": f"""
                    INCLUDE THE FOLLOWING HEADER IN YOUR MOTIVATION LETTER:\n
                    'Subject: Application for the position of {job.position} at {job.company}'\n
                    'From: {profile.name} on behalf of MareVisie B.v., Delft, Netherlands'\n

                    You are an assistant helping a candidate write a motivation letter for a job application.
                    The candidate is applying to the following position:\n
                    {job.position} at {job.company}.\n

                    The job has the following requirements:\n
                    {job.assignment.requirements}\n

                    The job requires the following skills:\n
                    {job.assignment.skills}\n

                    The job has the following preferences:\n
                    {job.assignment.preferences}\n
                    -------------------
                    The candidate, {profile.name}, has the following profile:\n
                    {profile.profile}\n

                    The candidate has the following experience:\n
                    {profile.experience}\n

                    The candidate has the following skills:\n
                    {profile.skills}\n
                    """,
            },
            {
                "role": "user",
                "content": "Write a motivation letter for the candidate in first person. The tone should be formal and professional Be concise.",
            },
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content


def profile_matcher(agent: Agent, profiles: ProfileManager, job: Job) -> str:

    # print(f"\ndebug-- Available Profiles: {profiles}\n")
    # print(f"\ndebug-- Position: {job.position}\n")
    # print(f"\ndebug-- Description: {job.assignment.description}\n")
    # print(f"\ndebug-- Requirements: {job.assignment.requirements}\n")
    # print(f"\ndebug-- Skills: {job.assignment.skills}\n")

    response = agent.client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": f"""
                    You are an assistant designed to match job openings to potential candidates.\n
                    BE EXTREMELY CRITICAL IN YOUR SELECTION. ONLY MATCH CANDIDATES IF THEY HAVE REQUIRED SKILLS.\n
                    RETURN **ONLY** THE NAME OF THE BEST MATCHING CANDIDATES (UP TO A MAXIMUM OF 3) FOR THE JOB.\n
                    The job is the following:\n
                    {job.position}.\n
                    The job has the following requirements:\n
                    {job.assignment.requirements}\n
                    The job requires the following skills:\n
                    {job.assignment.skills}\n
                    The job has the following preferences:\n
                    {job.assignment.preferences}\n
                    You have the following candidates:\n
                    {str(profiles)}\n
                    """,
            },
            {
                "role": "user",
                "content": "Return the name of the best matching candidates (up to a maximum of 3) for the job. Be critical in your selection. Format the output as:\n'Candidate 1,Candidate 2,Candidate 3'. If no candidates are available, return 'NO CANDIDATES FULLFILL JOB REQUIREMENTS\nEXPLANATION FOR WHY CANDIDATE 1 DOES NOT FULLFILL JOB REQUIREMENTS\nEXPLANATION FOR WHY CANDIDATE 2 DOES NOT FULLFILL JOB REQUIREMENTS\n etc.'.\n",
            },
        ],
        temperature=0.1,
    )

    # print(
    #     f"\nResponse Candidate Match for {job.position}: {response.choices[0].message.content}\n"
    # )

    return response.choices[0].message.content


def profile_from_names(names: str) -> Profile:
    profiles = []
    for name in names.split(","):
        profile = ProfileManager().get_profile(name)
        if profile:
            profiles.append(profile)

    return profiles

def get_profiles_from_match(agent: Agent, profiles: ProfileManager, job: Job) -> list[Profile]:
    names = profile_matcher(agent, profiles, job)
    profile_objs = profile_from_names(names)
    for profile in profile_objs:
        motivation_obj = Motivation(job, "")
        profile.add_job_match(motivation_obj)
    return profile_objs