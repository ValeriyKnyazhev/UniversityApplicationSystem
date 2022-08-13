from University import University
from Student import Student

class Agreement:

    def __init__(self, university: University, profile: str):
        self.university = university
        self.profile = profile

class ApplicationSystem:

    def __init__(self):
        # university -> list[profile]
        self.university_to_profiles = {}
        # university -> profile -> list[student]
        self.all_students_data = {}
        # student id -> Agreement (if not found, no agreement submitted at the moment)
        self.student_to_agreement = {}
        # student id -> university (if not found, student is still in process of admission)
        self.listed_students = {}
        # student id -> university -> profile -> score (all applications of each student with certain exam score)
        self.student_applications = {}
        # university -> profile -> number of places in university
        self.university_places_details = {}
        
        for university in University:
            self.university_to_profiles[university] = []
            self.all_students_data[university] = {}
            self.university_places_details[university] = {}