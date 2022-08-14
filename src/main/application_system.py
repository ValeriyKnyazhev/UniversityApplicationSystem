from ..core import *

from typing import Dict, List, Optional

from colorama import Fore, Style

class Agreement:

    def __init__(self, university: University, profile: str):
        self.university: University = university
        self.profile: str = profile


class ApplicationSystem:

    def __init__(self):
        # university -> list[profile]
        self.__university_to_profiles: Dict[University, List[str]] = {}
        # university -> profile -> list[student]
        self.__all_students_data: Dict[University, Dict[str, List[Student]]] = {}
        # student id -> Agreement (if not found, no agreement submitted at the moment)
        self.__student_to_agreement: Dict[str, Agreement] = {}
        # student id -> university (if not found, student is still in process of admission)
        self.__listed_students: Dict[str, University] = {}
        # student id -> university -> profile -> score (all applications of each student with certain exam score)
        self.__student_applications: Dict[str, Dict[University, Dict[str, int]]] = {}
        # university -> profile -> number of places in university
        self.__university_places_details: Dict[University, Dict[str, int]] = {}

        for university in University:
            self.__university_to_profiles[university] = []
            self.__all_students_data[university] = {}
            self.__university_places_details[university] = {}

    # university = University, profile = string, data = array[Student]
    def add_profile_students_data(self, university: University, profile: str, data: List[Student]):
        self.__university_to_profiles[university].append(profile)
        self.__all_students_data[university][profile] = data
        self.__university_places_details[university][profile] = 0
        for student in data:
            if student.agreement_submitted:
                self.__student_to_agreement[student.id] = Agreement(university, profile)
            if student.id in self.__student_applications:
                if university in self.__student_applications[student.id]:
                    if profile in self.__student_applications[student.id][university]:
                        print(Fore.RED + 'ERROR: student id={} is already registered for profile {} in university {}'
                              .format(student.id, profile, university.name) + Style.RESET_ALL)
                    else:
                        self.__student_applications[student.id][university][profile] = student.score
                else:
                    self.__student_applications[student.id][university] = {profile: student.score}
            else:
                self.__student_applications[student.id] = {university: {profile: student.score}}

    def get_chosen_university_for_student(self, student_id: str) -> Optional[University]:
        return self.__student_to_agreement[student_id].university if student_id in self.__student_to_agreement else None

    def is_student_applicable_to_university(self, student_id: str, university: University) -> bool:
        university_chosen = self.get_chosen_university_for_student(student_id)
        return university_chosen is None or university == university_chosen

    # ge means greater or equals
    # returns only that students who can apply for this profile in this university
    def get_all_students_where_score_ge_and_admission_possible(self, university: University, profile: str,
                                                               score: int) -> List[Student]:
        if profile in self.__university_to_profiles[university]:
            return [student for student in self.__all_students_data[university][profile] if
                    student.score >= score and self.is_student_applicable_to_university(student.id, university)]
        else:
            print(Fore.YELLOW + 'WARNING: profile {} not found for university {}'.format(profile, university.name)
                  + Style.RESET_ALL)
            return []

    # ge means greater or equals
    def get_all_students_where_score_ge(self, university: University, profile: str, score: int) -> List[Student]:
        if profile in self.__university_to_profiles[university]:
            return [student for student in self.__all_students_data[university][profile] if student.score >= score]
        else:
            print(Fore.YELLOW + 'WARNING: profile {} not found for university {}'.format(profile, university.name)
                  + Style.RESET_ALL)
            return []
