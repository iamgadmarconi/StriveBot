
from src.db import JobDAO, CandidateDAO
from src.scraper import Job
from src.profiles import ProfileManager
from src.utils import Agent
from src.agent import profile_matcher

agent = Agent()



# Usage Example:
dao = JobDAO()
candidate_dao = CandidateDAO()
profiles = ProfileManager().profiles
new_job = Job(agent=agent, url="https://striive.com/nl/opdrachten/ministerie-van-justitie-veiligheid-jenv/informatieanalist/23fee748-0273-4739-863d-35f3455e2cd8")

for candidate in profiles:
    candidate_dao.add_candidate(candidate)

dao.add_job(new_job)
print("done")