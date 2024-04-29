import os
from openai import OpenAI


class Agent:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)


def categorize_description(agent: Agent, text: str) -> dict:

    response = agent.client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": f"""
                    You are an assistant designed to categorize the text into 3 distinct categories:\n
                    - REQUIREMENTS\n (e.g. qualifications, experience, etc.)
                    - PREFERENCES\n (e.g. wishes, desires, etc.)
                    - SKILLS\n (e.g. competencies, abilities, etc.)

                    Be thorough in your categorization and ensure that you capture all relevant information.\n

                    FORMAT THE OUTPUT EXACTLY AS FOLLOWS:
                    
                    REQUIREMENTS
                    REQUIREMENT 1,REQUIREMENT 2, REQUIREMENT 3, etc.
                    PREFERENCES
                    PREFERENCE 1,PREFERENCE 2, PREFERENCE 3, etc.
                    SKILLS
                    SKILL 1,SKILL 2,SKILL 3, etc.
                    
                    note that the items in each category should be separated by commas.\n
                    The text to categorize is the following:\n
                    {text}\n
                    """,
            },
            {
                "role": "user",
                "content": "Categorize the text into different sections.",
            },
        ],
        temperature=0.1,
    )

    return parse_description_to_dict(response.choices[0].message.content)


def get_parameters_from_raw_description(agent: Agent, raw_description: str) -> dict:

    # print(
    #     f"Extracting parameters from the following job description:\n{raw_description}\n"
    # )

    response = agent.client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": f"""
                    You are an assistant designed to extract the parameters from a job description.\n
                    The parameters to extract are the following:\n
                    Commitment (in hours per week)
                    Location (city, country)
                    Max. Hourly rate (in EUR / hour [convert if necessary])
                    Job Start date (date, formatted as DD/MM/YYYY)
                    Job End date (date, formatted as DD/MM/YYYY)
                    Application Deadline (date, formatted as DD/MM/YYYY)
                    Job Submitter (name of the person submitting the job and contact details)\n

                    Be thorough in your extraction and ensure that you capture all relevant information.\n
                    FORMAT THE OUTPUT EXACTLY AS FOLLOWS:\n
                    
                    commitment:COMMITMENT
                    location:LOCATION
                    max_hourly_rate:MAX HOURLY RATE
                    start_date:START DATE
                    end_date:END DATE
                    deadline:DEADLINE

                    IF ANY OF THE PARAMETERS ARE NOT PRESENT IN THE TEXT, LEAVE THE FIELD EMPTY.\n

                    The text to extract the parameters from is the following:\n
                    {raw_description}\n
                    """,
            },
            {
                "role": "user",
                "content": "Extract the parameters from the job description. Format the output as specified.",
            },
        ],
        temperature=0.1,
    )

    # print(f"Parameters found:\n{response.choices[0].message.content}")

    return parse_parameters_to_dict(response.choices[0].message.content)


def clean_text(text: str):
    text = (
        text.replace("\n", " ")
        .replace("\r", " ")
        .replace("\t", " ")
        .replace("-", "")
        .replace("•", "")
        .strip()
    )

    return text


def parse_description_to_dict(text: str) -> dict:
    # Split the text into lines
    lines = text.splitlines()

    # Initialize an empty dictionary to hold the results
    result_dict = {}

    # Variable to keep track of the current key while iterating
    current_key = None

    # Iterate over each line in the list
    for line in lines:
        # Strip extra whitespace from the line
        line = line.strip()

        # Check if the line is one of the headers
        if line in ["REQUIREMENTS", "PREFERENCES", "SKILLS"]:
            current_key = line  # Update the current key
            result_dict[current_key] = ""  # Initialize an empty string for the key
        elif current_key:
            # If the key already has some data, add a comma before adding more
            if result_dict[current_key]:
                result_dict[current_key] += ", "
            # Add the current line (trimmed and cleaned of extra spaces around commas)
            result_dict[current_key] += ", ".join(
                item.strip() for item in line.split(",")
            )

    return result_dict


def parse_parameters_to_dict(text: str) -> dict:
    parsed_data = {}

    # Split the input string into lines
    lines = text.strip().split("\n")

    for line in lines:
        if line.strip():  # Check if the line is not empty
            # Split on the first colon only and allow splitting into at most 2 items
            parts = line.split(":", 1)
            key = parts[0].strip()
            value = (
                parts[1].strip() if len(parts) > 1 else None
            )  # Use None for empty values
            parsed_data[key] = (
                None if value == "" else value
            )  # Store None if value is empty

    return parsed_data


def pretty_print_matches(match: dict) -> None:
    string = f"""
    Profile matched for {match['Position']} at {match['Company']}:\n\n
    -------------------
    Profile Matched:{match['Candidate'].name}

    Motivation Letter:
    {match['Motivation']}

    -------------------
    """
    print(string)


def format_bulleted_list(text):
    """ Converts comma-separated text into a bulleted list formatted string. """
    if not text:
        return "Not specified"
    items = text.split(", ")
    bulleted_items = "\n".join(f"• {item}" for item in items if item.strip())
    return bulleted_items
