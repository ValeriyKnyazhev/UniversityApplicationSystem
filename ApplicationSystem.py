from University import University
from Student import Student

from typing import List

from colorama import Fore, Style

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

    # university = University, profile = string, data = array[Student]
    def add_profile_students_data(self, university: University, profile: str, data: List[Student]):
        self.university_to_profiles[university].append(profile)
        self.all_students_data[university][profile] = data
        self.university_places_details[university][profile] = 0
        for student in data:
            if student.agreement_submitted:
                self.student_to_agreement[student.id] = Agreement(university, profile)
            if student.id in self.student_applications:
                if university in self.student_applications[student.id]:
                    if profile in self.student_applications[student.id][university]:
                        print(Fore.RED + 'ERROR: student id={} is already registered for profile {} in university {}'
                              .format(student.id, profile, university.name) + Style.RESET_ALL)
                    else:
                        self.student_applications[student.id][university][profile] = student.score
                else:
                    self.student_applications[student.id][university] = {profile: student.score}
            else:
                self.student_applications[student.id] = {university: {profile: student.score}}
