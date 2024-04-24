from src.profiles import Profile, ProfileManager
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


def profile_matcher(agent: Agent, profiles: ProfileManager, job: Job) -> Profile:

    response = agent.client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": f"""
                    BE EXTREMELY CRITICAL IN YOUR SELECTION. ONLY MATCH CANDIDATES IF THEY HAVE ALL REQUIRED SKILLS.\n

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
                    """,
            },
            {
                "role": "user",
                "content": "Return the name of the best matching candidates (up to a maximum of 3) for the job. Be critical in your selection.",
            },
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content
