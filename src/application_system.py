from student import Student
from university import University

from statistics import mean, median, quantiles
from typing import Dict, List, Optional, Tuple

import pandas as pd
from IPython.display import display
from colorama import Fore, Style


class Agreement:

    def __init__(self, university: University, profile: str):
        self.university: University = university
        self.profile: str = profile


class ApplicationSystem:

    def __init__(self):
        # university -> list[profile]
        self.__university_to_profiles = {}
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

    # ge means greater or equals
    # returns only that students who can apply for this profile in this university
    def get_all_students_where_score_ge_and_admission_possible(self, university: University, profile: str,
                                                               score: int) -> List[Student]:
        if profile in self.__university_to_profiles[university]:
            return [student for student in self.__all_students_data[university][profile] if
                    student.score >= score and self.__is_student_applicable_to_university(student.id, university)]
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

    def get_current_min_scores(self) -> Dict[University, Dict[str, int]]:
        scores = {}
        for university in self.__all_students_data.keys():
            if university not in scores:
                scores[university] = {}
            for profile in self.__all_students_data[university].keys():
                min_score = self.__get_current_min_score(university, profile)
                scores[university][profile] = min_score
        return scores

    def get_current_positions(self, student_id: str) -> Dict[University, Dict[str, Tuple[int, int]]]:
        positions = {}
        if student_id in self.__student_applications:
            university_chosen = self.__get_chosen_university_for_student(student_id)
            print("chosen university is " + str(university_chosen))
            for university, profiles in self.__student_applications[student_id].items():
                if university not in positions:
                    positions[university] = {}
                if university_chosen is None or university == university_chosen:
                    for profile, score in profiles.items():
                        current_position = self.__get_current_position(student_id, university, profile)
                        positions[university][profile] = (current_position, score)
            return positions
        else:
            print(Fore.YELLOW + "WARNING: student id={} not found".format(student_id) + Style.RESET_ALL)
            return positions

    # All agreements number in all universities
    def showNumberOfAgreementsByUniversity(self):
        counts = {}
        for university in University:
            counts[university] = 0
        for student, agreement in self.__student_to_agreement.items():
            counts[agreement.university] += 1

        df = pd.DataFrame(data={'University': [u.value for u in counts.keys()], 'Agreements': counts.values()})
        df = df.style.set_caption('All agreements (with listed)')
        df.index += 1
        display(df)

    # All pending (not yet listed) agreements number in all universities
    def showNumberOfPendingAgreementsByUniversity(self):
        counts = {}
        for university in University:
            counts[university] = 0
        for student, agreement in self.__student_to_agreement.items():
            if student not in self.__listed_students:
                counts[agreement.university] += 1

        df = pd.DataFrame(data={'University': [u.value for u in counts.keys()], 'Agreements': counts.values()})
        df = df.style.set_caption('All pending agreements')
        df.index += 1
        display(df)

    # Math statistics by universities
    def agreementsStatisticsByUniversities(self):
        scores = {}
        for university in self.__all_students_data.keys():
            scores[university] = {}

        for university in self.__all_students_data.keys():
            for students in self.__all_students_data[university].values():
                for student in students:
                    if student.id in self.__student_to_agreement and \
                            self.__student_to_agreement[student.id].university == university and \
                            student.id not in self.__listed_students:
                        scores[university][student.id] = student.score

        result = []
        for university, data in scores.items():
            university_scores = list(data.values())
            if len(university_scores) < 2:
                continue
            percentiles = quantiles(university_scores, n=100)
            result.append([university.value, len(university_scores), mean(university_scores),
                           median(university_scores), percentiles[94], percentiles[89], percentiles[79]])

        df = pd.DataFrame(result, columns=['University', 'N of Agreements', 'Average score',
                                           'Median score', 'Top 5% score', 'Top 10% score', 'Top 20% score'])
        df = df.round(1)
        df.index += 1
        display(df)

    # Math statistics by universities and profiles
    def agreementsStatisticsByUniversitiesAndProfiles(self):
        scores = {}

        for university in self.__all_students_data.keys():
            scores[university] = {}
            for profile, students in self.__all_students_data[university].items():
                scores[university][profile] = {}
                for student in students:
                    if student.id in self.__student_to_agreement and \
                            self.__student_to_agreement[student.id].university == university and \
                            self.__student_to_agreement[student.id].profile == profile and \
                            student.id not in self.__listed_students:
                        scores[university][profile][student.id] = student.score

        result = []
        for u, d1 in scores.items():
            for p, d2 in d1.items():
                u_scores = list(d2.values())
                if len(u_scores) < 2:
                    continue
                percentiles = quantiles(u_scores, n=100)
                result.append([u.value, p, len(u_scores), mean(u_scores), median(u_scores),
                               percentiles[94], percentiles[89], percentiles[79]])

        df = pd.DataFrame(result, columns=['University', 'Profile', 'N of Agreements', 'Average score',
                                           'Median score','Top 5% score', 'Top 10% score', 'Top 20% score'])
        df = df.round(1)
        df.index += 1
        display(df)

    def __get_current_min_score(self, university: University, profile: str) -> int:
        n_places = self.__university_places_details[university][profile]
        students = self.__all_students_data[university][profile]

        applicable_students = [student for student in students if
                               self.__is_student_applicable_to_university(student.id, university) and
                               student.id not in self.__listed_students]

        if n_places == 0:
            return 0
        elif not applicable_students:
            print(Fore.RED + "Not found students for {} in {}".format(profile, university) + Style.RESET_ALL)
            return -1
        elif len(applicable_students) < n_places:
            print(Fore.YELLOW + "Found less students than places for {} in {}".format(profile, university)
                  + Style.RESET_ALL)
            return applicable_students[-1].score
        else:
            return applicable_students[n_places - 1].score

    def __get_current_position(self, student_id: str, university: University, profile: str) -> int:
        current_position = 0
        if profile in self.__university_to_profiles[university]:
            if student_id in self.__student_applications and university in self.__student_applications[student_id] \
                    and profile in self.__student_applications[student_id][university]:
                for student in self.__all_students_data[university][profile]:
                    if self.__is_student_applicable_to_university(student_id, university):
                        if student.id not in self.__listed_students:
                            current_position += 1
                        if student.id == student_id:
                            return current_position
            else:
                print(Fore.YELLOW + "WARNING: student didn't apply for profile {} not found for university {}"
                      .format(profile, university.name) + Style.RESET_ALL)
                return current_position
        else:
            print(Fore.YELLOW + "WARNING: profile {} not found for university {}".format(profile, university.name)
                  + Style.RESET_ALL)
            return current_position

    def __is_student_applicable_to_university(self, student_id: str, university: University) -> bool:
        university_chosen = self.__get_chosen_university_for_student(student_id)
        return university_chosen is None or university == university_chosen

    def __get_chosen_university_for_student(self, student_id: str) -> Optional[University]:
        return self.__student_to_agreement[student_id].university if student_id in self.__student_to_agreement else None
