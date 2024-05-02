# StriveBot

StriveBot is a Bot that scrapes Striive for jobs and categorizes them based on requirements. StriveBot supports automatic candidate matching and motivation letter generation using OpenAI's API.

## Table of Contents

1. Installation and setup.
2. Usage

## Installation and setup

### Installation

To install StriveBot, you can either download the executable file from the releases page, or clone this repository, download `requirements.txt`, and run `main.py`.

### Setup

You will need to enter `OPENAI_API_KEY` placed in a `.env` to use the program. To setup candidates, you can add them to `src/candidates/candidates.csv` in the same format as the examples. You should also add the CV's of the candidates as a PDF file called: `firstname_middlename_lastname.pdf`.

## Usage

Open the app and press "Start Search" to begin scraping for jobs. You can specify a keyword to search for a specific keyword, or enter a URL to scrape a specific posting. You can select jobs either for export to CSV (found in `src\jobs\example.csv`), or match candidates to them by pressing "Match Candidates". Clicking on a Job will open details, including any matched candidates. Here you have the option to generate Motivation letters for that Job for any mathching candidates. You can view generated motivation letters by pressing on the Candidate.
