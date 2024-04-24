import os
from openai import OpenAI


class Agent:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)


def categorize_description(agent: Agent, text: str) -> dict:
    cleaned_text = clean_text(text)

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

                    FORMAT THE OUTPUT EXACTLY AS FOLLOWS:\n
                    '
                    REQUIREMENTS
                    REQUIREMENT 1,REQUIREMENT 2, REQUIREMENT 3
                    PREFERENCES
                    PREFERENCE 1,PREFERENCE 2, PREFERENCE 3
                    SKILLS
                    SKILL 1,SKILL 2,SKILL 3
                    '\n
                    note that the items in each category should be separated by commas.\n
                    The text to categorize is the following:\n
                    {cleaned_text}\n
                    """,
            },
            {
                "role": "user",
                "content": "Categorize the text into different sections.",
            },
        ],
        temperature=0.1,
    )

    return parse_text_to_dict(response.choices[0].message.content)


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


def parse_text_to_dict(text):
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
