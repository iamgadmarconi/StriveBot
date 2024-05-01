
from db.db import JobDAO, CandidateDAO, MotivationDAO
from src.scraper import Job
from src.profiles import ProfileManager
from src.utils import Agent
from src.agent import get_profiles_from_match

agent = Agent()



# Usage Example:
dao = JobDAO()
candidate_dao = CandidateDAO()
motivation_dao = MotivationDAO()

profiles = ProfileManager()
new_job = Job(agent=agent, url="https://striive.com/nl/opdrachten/centraal-bureau-voor-de-statistiek-cbs/vmware-specialist/d830c5bc-bc45-4d61-b6c9-4b236f026af7")

for candidate in profiles.profiles:
    candidate_dao.add_candidate(candidate)

matches = get_profiles_from_match(agent, profiles, new_job)
if matches:
    for match in matches:
        motivation_dao.add_motivation(new_job.id, match.id, "This is a test motivation letter")

dao.add_job(new_job)
print("done")