from dotenv import load_dotenv

from src.profiles import ProfileManager
from src.scraper import Job
from src.agent import Agent

load_dotenv()

def main():
    profiles = ProfileManager()
    print(profiles)

    position = "Software Engineer"
    description = "We are looking for a software engineer to join our team. The ideal candidate will have experience with Python, and C++. The candidate should have a strong understanding of algorithms and data structures. The candidate should have experience with web development and cloud technologies. The candidate should have excellent communication skills and be a team player."
    skills = "Python, C++, Algorithms, Data Structures, Web Development, Cloud Technologies, Communication, Team Player"
    
    job = Job(position, description, skills)

    agent = Agent()

    name = agent.profile_matcher(profiles, job)
    candidate = profiles.get_profile(name)

    print(agent.motivation_letter(candidate, job))


if __name__ == "__main__":
    main()