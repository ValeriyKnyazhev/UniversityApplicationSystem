from University import University
from Student import Student

from typing import List, Optional

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

    def get_chosen_university_for_student(self, student_id: str) -> Optional[University]:
        return self.student_to_agreement[student_id].university if student_id in self.student_to_agreement else None

    def is_student_applicable_to_university(self, student_id: str, university: University) -> bool:
        university_chosen = self.get_chosen_university_for_student(student_id)
        return university_chosen is None or university == university_chosen

    # ge means greater or equals
    # returns only that students who can apply for this profile in this university
    def get_all_students_where_score_ge_and_admission_possible(self, university: University, profile: str,
                                                               score: int) -> List[Student]:
        if profile in self.university_to_profiles[university]:
            return [student for student in self.all_students_data[university][profile] if
                    student.score >= score and self.is_student_applicable_to_university(student.id, university)]
        else:
            print(Fore.YELLOW + 'WARNING: profile {} not found for university {}'.format(profile, university.name)
                  + Style.RESET_ALL)
            return []

    # ge means greater or equals
    def get_all_students_where_score_ge(self, university: University, profile: str, score: int) -> List[Student]:
        if profile in self.university_to_profiles[university]:
            return [student for student in self.all_students_data[university][profile] if student.score >= score]
        else:
            print(Fore.YELLOW + 'WARNING: profile {} not found for university {}'.format(profile, university.name)
                  + Style.RESET_ALL)
            return []
