from bs4 import BeautifulSoup
import spacy
import en_core_web_sm

class Job:
    def __init__(self, position, description, skills):
        self.position = position
        self.description = description
        self.skills = skills
