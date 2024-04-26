import os
import csv

from src.scraper import Job


def save_job_to_csv(job: Job, force: bool = False) -> None:
    headers = [
        "Position",
        "Start date",
        "End date",
        "Max. Hourly rate",
        "Hours/week",
        "Location",
        "Deadline",
        "Company",
        "Submitter",
        "Status",
        "Candidate",
        "URL",
        "Description",
    ]
    file_name = f"src\\jobs\\{job.position}_{job.company}.csv"

    if not os.path.exists(file_name) or force:
        with open(file_name, "w", newline="") as file:
            writer = csv.writer(file, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
            writer.writerow(headers)

    new_data = [
        job.position,
        job.start,
        job.end,
        job.max_hourly_rate,
        job.commitment,
        job.location,
        job.deadline,
        job.company,
        job.submitter,
        job.status,
        job.candidates,
        job.url,
        job.assignment,
    ]
    with open(file_name, "a", newline="") as file:
        writer = csv.writer(file, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(new_data)

    print(f"Data saved to '{file_name}'.")
