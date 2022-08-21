from src.core import Profile, StudentId, Student, University

from statistics import mean, median, quantiles

from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from IPython.display import display

from colorama import Fore, Style

from dataclasses import dataclass


@dataclass(eq=True, order=True)
class Agreement:
    university: University
    profile: Profile


class ApplicationSystem:

    def __init__(self):
        self.__university_to_profiles: Dict[University, List[Profile]] = {}
        self.__all_students_data: Dict[University, Dict[Profile, List[Student]]] = {}
        # if not found, no agreement submitted at the moment
        self.__student_to_agreement: Dict[StudentId, Agreement] = {}
        # if not found, student is still in process of admission
        self.__listed_students: Dict[StudentId, University] = {}
        # all applications of each student with certain exam score
        self.__student_applications: Dict[StudentId, Dict[University, Dict[Profile, int]]] = {}
        # number of places in university
        self.__university_places_details: Dict[University, Dict[Profile, int]] = {}

        for university in University:
            self.__university_to_profiles[university]: List[Profile] = []
            self.__all_students_data[university]: Dict[Profile, List[Student]] = {}
            self.__university_places_details[university]: Dict[Profile, int] = {}

    def add_profile_students_data(self, university: University, profile: Profile, data: List[Student]):
        self.__university_to_profiles[university].append(profile)
        self.__all_students_data[university][profile]: List[Student] = data
        self.__university_places_details[university][profile]: int = 0
        for student in data:
            if student.agreement_submitted:
                self.__student_to_agreement[student.id]: Agreement = Agreement(university, profile)
            if student.id in self.__student_applications:
                if university in self.__student_applications[student.id]:
                    if profile in self.__student_applications[student.id][university]:
                        print(
                            Fore.RED + f"ERROR: student id={student} is already registered for profile {profile} in university {university}" + Style.RESET_ALL)
                    else:
                        self.__student_applications[student.id][university][profile]: int = student.score
                else:
                    self.__student_applications[student.id][university]: Dict[Profile, int] = {profile: student.score}
            else:
                self.__student_applications[student.id]: Dict[University, Dict[Profile, int]] = {
                    university: {profile: student.score}
                }

    def add_places_details(self, places_details: Dict[University, Dict[Profile, int]]):
        self.__university_places_details: Dict[University, Dict[Profile, int]] = places_details

    def add_listed_students(self, data: Dict[StudentId, Tuple[University, str]]):
        for student_id, agreement in data.items():
            self.__student_to_agreement[student_id]: Agreement = Agreement(agreement[0],
                                                                           Profile(f"listed by {agreement[1]}"))
            self.__listed_students[student_id]: University = agreement[0]

    # ge means greater or equals
    # returns only that students who can apply for this profile in this university
    def get_all_students_where_score_ge_and_admission_possible(self, university: University, profile: Profile,
                                                               score: int) -> List[Student]:
        if profile in self.__university_to_profiles[university]:
            return [student for student in self.__all_students_data[university][profile] if
                    student.score >= score and self.__is_student_applicable_to_university(student.id, university)]
        else:
            print(
                Fore.YELLOW + f"WARNING: profile {profile} not found for university {university}" + Style.RESET_ALL)
            return []

    # ge means greater or equals
    def get_all_students_where_score_ge(self, university: University, profile: Profile, score: int) -> List[Student]:
        if profile in self.__university_to_profiles[university]:
            return [student for student in self.__all_students_data[university][profile] if student.score >= score]
        else:
            print(
                Fore.YELLOW + f"WARNING: profile {profile} not found for university {university}" + Style.RESET_ALL)
            return []

    def show_all_students_with_score_ge_and_their_agreement(self, university: University, profile: Profile, score: int):
        students: List[Student] = self.get_all_students_where_score_ge(university, profile, score)
        df = pd.DataFrame([[student.id, student.score,
                            self.__student_to_agreement[student.id].university if
                            student.id in self.__student_to_agreement else "",
                            self.__student_to_agreement[student.id].profile if
                            student.id in self.__student_to_agreement else ""]
                           for student in students],
                          columns=['Id', 'Score', "Chosen University", "Chosen Profile"])
        df.index += 1
        display(df)

    def show_all_students_with_score_ge_and_admission_possible(self, university: University, profile: Profile,
                                                               score: int):
        students: List[Student] = self.get_all_students_where_score_ge_and_admission_possible(university, profile,
                                                                                              score)
        df = pd.DataFrame([[student.id, student.score,
                            self.__student_to_agreement[student.id].profile if
                            student.id in self.__student_to_agreement else ""]
                           for student in students],
                          columns=['Id', 'Score', f"Chosen Profile in {university}"])
        df.index += 1
        display(df)

    def get_current_min_scores(self) -> Dict[University, Dict[Profile, int]]:
        scores: Dict[University, Dict[Profile, int]] = {}
        for university in self.__all_students_data.keys():
            if university not in scores:
                scores[university]: Dict[Profile, int] = {}
            for profile in self.__all_students_data[university].keys():
                min_score: int = self.__get_current_min_score(university, profile)
                scores[university][profile]: int = min_score
        return scores

    def get_current_positions(self, student_id: StudentId) -> Dict[University, Dict[Profile, Tuple[int, int]]]:
        positions: Dict[University, Dict[Profile, Tuple[int, int]]] = {}
        if student_id in self.__student_applications:
            for university, profiles in self.__student_applications[student_id].items():
                if university not in positions:
                    positions[university]: Dict[Profile, Tuple[int, int]] = {}
                if self.__is_student_applicable_to_university(student_id, university):
                    for profile, score in profiles.items():
                        current_position: int = self.__get_current_position(student_id, university, profile)
                        positions[university][profile]: Tuple[int, int] = (current_position, score)
            return positions
        else:
            print(Fore.YELLOW + f"WARNING: student id={student_id} not found" + Style.RESET_ALL)
            return positions

    # All agreements number in all universities
    def show_number_of_agreements_by_university(self):
        counts: Dict[University, int] = {}
        for university in University:
            counts[university]: int = 0
        for student, agreement in self.__student_to_agreement.items():
            counts[agreement.university] += 1

        df = pd.DataFrame(data={'University': [u.value for u in counts.keys()], 'Agreements': counts.values()})
        df = df.style.set_caption('All agreements (with listed)')
        df.index += 1
        display(df)

    # All pending (not yet listed) agreements number in all universities
    def show_number_of_pending_agreements_by_university(self):
        counts: Dict[University, int] = {}
        for university in University:
            counts[university]: int = 0
        for student, agreement in self.__student_to_agreement.items():
            if student not in self.__listed_students:
                counts[agreement.university] += 1

        df = pd.DataFrame(data={'University': [u.value for u in counts.keys()], 'Agreements': counts.values()})
        df = df.style.set_caption('All pending agreements')
        df.index += 1
        display(df)

    # Math statistics by universities
    def show_agreements_statistics_by_universities(self):
        scores: Dict[University, Dict[StudentId, int]] = {}
        for university in self.__all_students_data.keys():
            scores[university]: Dict[StudentId, int] = {}

        for university in self.__all_students_data.keys():
            for students in self.__all_students_data[university].values():
                for student in students:
                    if student.id in self.__student_to_agreement and \
                            self.__student_to_agreement[student.id].university == university and \
                            student.id not in self.__listed_students:
                        scores[university][student.id]: int = student.score

        result: List[List[Any]] = []
        for university, data in scores.items():
            university_scores: List[int] = list(data.values())
            if len(university_scores) < 2:
                continue
            percentiles: List[int] = quantiles(university_scores, n=100)
            result.append([university.value, len(university_scores), mean(university_scores),
                           median(university_scores), percentiles[94], percentiles[89], percentiles[79]])

        df = pd.DataFrame(result, columns=['University', 'N of Agreements', 'Average score',
                                           'Median score', 'Top 5% score', 'Top 10% score', 'Top 20% score'])
        df = df.round(1)
        df.index += 1
        display(df)

    # Math statistics by universities and profiles
    def show_agreements_statistics_by_universities_and_profiles(self):
        scores: Dict[University, Dict[Profile, Dict[StudentId, int]]] = {}

        for university in self.__all_students_data.keys():
            scores[university]: Dict[Profile, Dict[StudentId, int]] = {}
            for profile, students in self.__all_students_data[university].items():
                scores[university][profile]: Dict[StudentId, int] = {}
                for student in students:
                    if student.id in self.__student_to_agreement and \
                            self.__student_to_agreement[student.id].university == university and \
                            self.__student_to_agreement[student.id].profile == profile and \
                            student.id not in self.__listed_students:
                        scores[university][profile][student.id]: int = student.score

        result: List[List[Any]] = []
        for university in scores.keys():
            for profile, data in scores[university].items():
                university_scores: List[int] = list(data.values())
                if len(university_scores) < 2:
                    continue
                percentiles: List[int] = quantiles(university_scores, n=100)
                result.append([university.value, profile, len(university_scores), mean(university_scores),
                               median(university_scores), percentiles[94], percentiles[89], percentiles[79]])

        df = pd.DataFrame(result, columns=['University', 'Profile', 'N of Agreements', 'Average score',
                                           'Median score', 'Top 5% score', 'Top 10% score', 'Top 20% score'])
        df = df.round(1)
        df.index += 1
        display(df)

    def show_current_situation_for(self, student_id: StudentId):
        positions: Dict[University, Dict[Profile, Tuple[int, int]]] = self.get_current_positions(student_id)
        min_scores: Dict[University, Dict[Profile, int]] = self.get_current_min_scores()

        universities_and_profiles: List[Tuple[University, Profile]] = []
        for university in self.__student_applications[student_id].keys():
            for profile in self.__student_applications[student_id][university].keys():
                universities_and_profiles.append((university, profile))

        data: List[List[Any]] = []
        for d in universities_and_profiles:
            university: University = d[0]
            profile: Profile = d[1]
            if self.__is_student_applicable_to_university(student_id, university):
                position_data: Tuple[int, int] = positions[university][profile]
                min_score: int = min_scores[university][profile]
                number_of_places: int = self.__university_places_details[university][profile]
                data.append([university, profile, position_data[0], number_of_places, position_data[1], min_score])

        df = pd.DataFrame(data, columns=['University', 'Profile', 'Current Position',
                                         'Number of Places', 'Score', 'Min Score'])
        df.index += 1
        display(df)

    def __get_current_min_score(self, university: University, profile: Profile) -> int:
        n_places: int = self.__university_places_details[university][profile]
        students: List[Student] = self.__all_students_data[university][profile]

        applicable_students: List[Student] = [student for student in students if
                                              self.__is_student_applicable_to_university(student.id, university) and
                                              student.id not in self.__listed_students]

        if n_places == 0:
            return 0
        elif not applicable_students:
            print(Fore.RED + f"Not found students for {profile} in {university}" + Style.RESET_ALL)
            return -1
        elif len(applicable_students) < n_places:
            print(Fore.YELLOW + "Found less students than places for {} in {}".format(profile, university)
                  + Style.RESET_ALL)
            return applicable_students[-1].score
        else:
            return applicable_students[n_places - 1].score

    def __get_current_position(self, student_id: StudentId, university: University, profile: Profile) -> int:
        current_position: int = 0
        if profile in self.__university_to_profiles[university]:
            if student_id in self.__student_applications and \
                    university in self.__student_applications[student_id] and \
                    profile in self.__student_applications[student_id][university]:
                for student in self.__all_students_data[university][profile]:
                    if self.__is_student_applicable_to_university(student.id, university):
                        if student.id not in self.__listed_students:
                            current_position += 1
                        if student.id == student_id:
                            return current_position
            else:
                print(
                    Fore.YELLOW + f"WARNING: student didn't apply for profile {profile} not found for university {university}" + Style.RESET_ALL)
                return current_position
        else:
            print(Fore.YELLOW + f"WARNING: profile {profile} not found for university {university}" + Style.RESET_ALL)
            return current_position

    def __is_student_applicable_to_university(self, student_id: StudentId, university: University) -> bool:
        university_chosen: Optional[University] = self.__get_chosen_university_for_student(student_id)
        return university_chosen is None or university == university_chosen

    def __get_chosen_university_for_student(self, student_id: StudentId) -> Optional[University]:
        return self.__student_to_agreement[student_id].university if student_id in self.__student_to_agreement else None
