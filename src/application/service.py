from src.core import Profile, StudentId, Student, University
from src.utils.logger import CustomLogger

from dataclasses import dataclass
from statistics import mean, median, quantiles
from typing import Dict, List, NoReturn, Optional, Tuple


@dataclass(eq=True, order=True)
class Agreement:
    university: University
    profile: Profile


class ApplicationService:

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

        self.__logger: CustomLogger = CustomLogger(self.__class__.__name__)

    def add_profile_students_data(self, university: University, profile: Profile, data: List[Student]) -> NoReturn:
        self.__university_to_profiles[university].append(profile)
        self.__all_students_data[university][profile]: List[Student] = data
        self.__university_places_details[university][profile]: int = 0
        for student in data:
            if student.agreement_submitted:
                self.__student_to_agreement[student.id] = Agreement(university, profile)
            if student.id in self.__student_applications:
                if university in self.__student_applications[student.id]:
                    if profile in self.__student_applications[student.id][university]:
                        self.__logger.debug(
                            "Student id=%s is already registered for profile %s in university %s.",
                            student.id, profile, university
                        )
                    else:
                        self.__student_applications[student.id][university][profile] = student.score
                else:
                    self.__student_applications[student.id][university] = {profile: student.score}
            else:
                self.__student_applications[student.id] = {university: {profile: student.score}}

    def add_places_details(self, places_details: Dict[University, Dict[Profile, int]]) -> NoReturn:
        for university in places_details.keys():
            for profile, n_places in places_details[university].items():
                self.__university_places_details[university][profile] = n_places

    def add_listed_students(self, data: Dict[StudentId, Tuple[University, str]]) -> NoReturn:
        for student_id, agreement in data.items():
            university: University = agreement[0]
            self.__student_to_agreement[student_id] = Agreement(university, Profile(f"listed by {agreement[1]}"))
            self.__listed_students[student_id] = university

    def is_profile_application_uploaded(self, university: University, profile: Profile) -> bool:
        return profile in self.__university_to_profiles[university]

    def get_all_students_with_agreement_where_score_ge(
            self, university: University, profile: Profile, score: int) -> \
            List[Tuple[StudentId, int, University, Profile]]:
        """
        Returns only those students for whom the following conditions are met:
        - who has score greater or equals provided value
        Provides current submitted agreement (if found).
        """
        students: List[Student] = self.__get_all_students_where_score_ge(university, profile, score)
        return [
            (
                student.id,
                student.score,
                self.__student_to_agreement[student.id].university
                if student.id in self.__student_to_agreement else "",
                self.__student_to_agreement[student.id].profile
                if student.id in self.__student_to_agreement else ""
            ) for student in students
        ]

    def get_all_students_with_chosen_profile_where_score_ge_and_admission_possible(
            self, university: University, profile: Profile, score: int) -> List[Tuple[StudentId, int, Profile]]:
        """
        Returns only those students for whom the following conditions are met:
        - who can apply for this profile in this university
        - who has score greater or equals provided value
        Provides current chosen profile in university (if found).
        """
        students: List[Student] = self.__get_all_students_where_score_ge_and_admission_possible(
            university, profile, score
        )
        return [
            (
                student.id,
                student.score,
                self.__student_to_agreement[student.id].profile if student.id in self.__student_to_agreement else ""
            ) for student in students
        ]

    def get_universities_statistics(self) -> List[Tuple[University, int, float, float, float, float, float]]:
        """Returns statistics about number of agreements and score percentiles by universities"""
        scores: Dict[University, Dict[StudentId, int]] = {}
        for university in self.__all_students_data.keys():
            scores[university]: Dict[StudentId, int] = {}

        for university in self.__all_students_data.keys():
            for students in self.__all_students_data[university].values():
                for student in students:
                    if self.__is_student_applicable_to_university(student.id, university) and \
                            student.id not in self.__listed_students:
                        scores[university][student.id] = student.score

        result: List[Tuple[University, int, float, float, float, float, float]] = []
        for university, data in scores.items():
            university_scores: List[int] = list(data.values())
            if len(university_scores) < 2:
                continue
            percentiles: List[float] = quantiles(university_scores, n=100)
            result.append((
                university, len(university_scores), mean(university_scores),
                median(university_scores), percentiles[79], percentiles[89], percentiles[94]
            ))
        return result

    def get_profiles_statistics(self) -> List[Tuple[University, Profile, int, int, float, float, float, float, float]]:
        """
        Returns statistics about number of agreements, current minimal score and agreements score percentiles
        by universities and profiles
        """
        scores: Dict[University, Dict[Profile, Dict[StudentId, int]]] = {}
        for university in self.__all_students_data.keys():
            scores[university]: Dict[Profile, Dict[StudentId, int]] = {}
            for profile, students in self.__all_students_data[university].items():
                scores[university][profile]: Dict[StudentId, int] = {}
                for student in students:
                    if self.__is_student_applicable_to_university(student.id, university) and \
                            student.id not in self.__listed_students:
                        scores[university][profile][student.id] = student.score

        min_scores: Dict[University, Dict[Profile, int]] = self.__get_current_min_scores()

        result: List[Tuple[University, Profile, int, int, float, float, float, float, float]] = []
        for university in scores.keys():
            for profile, data in scores[university].items():
                university_scores: List[int] = list(data.values())
                if len(university_scores) < 2:
                    continue
                percentiles: List[float] = quantiles(university_scores, n=100)
                min_score: int = min_scores[university][profile]
                result.append((
                    university, profile, len(university_scores), min_score, mean(university_scores),
                    median(university_scores), percentiles[79], percentiles[89], percentiles[94]
                ))
        return result

    def get_number_of_agreements_by_university(self) -> Dict[University, int]:
        """All agreements number in all universities"""
        counts: Dict[University, int] = {}
        for university in University:
            counts[university] = 0
        for student, agreement in self.__student_to_agreement.items():
            counts[agreement.university] += 1
        return counts

    def get_number_of_pending_agreements_by_university(self) -> Dict[University, int]:
        """All pending (not yet listed) agreements number in all universities"""
        counts: Dict[University, int] = {}
        for university in University:
            counts[university] = 0
        for student, agreement in self.__student_to_agreement.items():
            if student not in self.__listed_students:
                counts[agreement.university] += 1
        return counts

    def get_applications_details_for(self, student_id: StudentId) -> \
            List[Tuple[University, Profile, int, int, int, int]]:
        """Returns details for all applications of student at the moment"""
        if student_id not in self.__student_applications:
            self.__logger.warn("Student id=%s not found.", student_id)
            return []

        positions: Dict[University, Dict[Profile, Tuple[int, int]]] = self.__get_current_positions(student_id)
        min_scores: Dict[University, Dict[Profile, int]] = self.__get_current_min_scores()

        universities_and_profiles: List[Tuple[University, Profile]] = []
        for university in self.__student_applications[student_id].keys():
            for profile in self.__student_applications[student_id][university].keys():
                universities_and_profiles.append((university, profile))

        data: List[Tuple[University, Profile, int, int, int, int]] = []
        for university, profile in universities_and_profiles:
            if self.__is_student_applicable_to_university(student_id, university):
                position_data: Tuple[int, int] = positions[university][profile]
                min_score: int = min_scores[university][profile]
                number_of_places: int = self.__university_places_details[university][profile]
                data.append((university, profile, position_data[0], number_of_places, position_data[1], min_score))
        return data

    def __get_all_students_where_score_ge_and_admission_possible(self, university: University, profile: Profile,
                                                                 score: int) -> List[Student]:
        if profile in self.__university_to_profiles[university]:
            return [student for student in self.__all_students_data[university][profile] if
                    student.score >= score and self.__is_student_applicable_to_university(student.id, university)]
        else:
            self.__logger.warn("Profile %s not found for university %s.", profile, university)
            return []

    def __get_all_students_where_score_ge(self, university: University, profile: Profile, score: int) -> List[Student]:
        if profile in self.__university_to_profiles[university]:
            return [student for student in self.__all_students_data[university][profile] if student.score >= score]
        else:
            self.__logger.warn("Profile %s not found for university %s.", profile, university)
            return []

    def __get_current_min_scores(self) -> Dict[University, Dict[Profile, int]]:
        scores: Dict[University, Dict[Profile, int]] = {}
        for university in self.__all_students_data.keys():
            if university not in scores:
                scores[university]: Dict[Profile, int] = {}
            for profile in self.__all_students_data[university].keys():
                min_score: int = self.__get_current_min_score(university, profile)
                scores[university][profile] = min_score
        return scores

    def __get_current_positions(self, student_id: StudentId) -> Dict[University, Dict[Profile, Tuple[int, int]]]:
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
            self.__logger.warn("Student id=%s not found.", student_id)
            return positions

    def __get_current_min_score(self, university: University, profile: Profile) -> int:
        n_places: int = self.__university_places_details[university][profile]
        students: List[Student] = self.__all_students_data[university][profile]

        applicable_students: List[Student] = [student for student in students if
                                              self.__is_student_applicable_to_university(student.id, university) and
                                              student.id not in self.__listed_students]

        if n_places == 0:
            return 0
        elif not applicable_students:
            self.__logger.error("Students for profile %s in university %s not found.", profile, university)
            return -1
        elif len(applicable_students) < n_places:
            self.__logger.warn("Found less students than places for profile %s in university %s.",
                               profile, university)
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
                self.__logger.warn("Student id=%s didn't apply for profile %s in university %s.",
                                   student_id, profile, university)
                return current_position
        else:
            self.__logger.warn("Profile %s not found for university %s.", profile, university)
            return current_position

    def __is_student_applicable_to_university(self, student_id: StudentId, university: University) -> bool:
        university_chosen: Optional[University] = self.__get_chosen_university_for_student(student_id)
        return university_chosen is None or university == university_chosen

    def __get_chosen_university_for_student(self, student_id: StudentId) -> Optional[University]:
        return self.__student_to_agreement[student_id].university if student_id in self.__student_to_agreement else None
