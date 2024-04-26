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
        "Candidate/Motivation",
        "URL",
        "Description",
    ]

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

    file_name = f"src\\jobs\\{job.position}_{job.company}.csv"

    file_exists = os.path.exists(file_name)

    # Open the file in the appropriate mode and write headers if necessary
    with open(file_name, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";", quoting=csv.QUOTE_ALL)
        if not file_exists or force:
            writer.writerow(headers)

        writer.writerow(new_data)

    print(f"Data saved to '{file_name}'.")
