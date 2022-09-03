from src.core import Profile, StudentId, University
from src.application import ApplicationService

from typing import NoReturn

import pandas as pd
from IPython.display import display

pd.set_option("display.max_rows", None)


class DataVisualizer:

    def __init__(self, service: ApplicationService):
        self.__service = service

    def show_all_students_and_agreement_where_score_ge(self,
                                                       university: University,
                                                       profile: Profile,
                                                       score: int) -> NoReturn:
        data = self.__service.get_all_students_with_agreement_where_score_ge(
            university, profile, score
        )

        df = pd.DataFrame(data, columns=['Id', 'Score', "Chosen University", "Chosen Profile"])
        df.index += 1
        display(df)

    def show_all_students_and_chosen_profile_where_score_ge_and_admission_possible(self,
                                                                                   university: University,
                                                                                   profile: Profile,
                                                                                   score: int) -> NoReturn:
        data = self.__service.get_all_students_with_chosen_profile_where_score_ge_and_admission_possible(
            university, profile, score
        )

        df = pd.DataFrame(data, columns=['Id', 'Score', f"Chosen Profile in {university}"])
        df.index += 1
        display(df)

    def show_agreements_distribution(self) -> NoReturn:
        data = self.__service.get_number_of_agreements_by_university()

        df = pd.DataFrame(data={'University': [u.value for u in data.keys()], 'Agreements': data.values()})
        df.style.set_caption('All agreements (with listed)')
        df.index += 1
        display(df)

    def show_pending_agreements_distribution(self) -> NoReturn:
        data = self.__service.get_number_of_pending_agreements_by_university()

        df = pd.DataFrame(data={'University': [u.value for u in data.keys()], 'Agreements': data.values()})
        df.style.set_caption('All pending agreements')
        df.index += 1
        display(df)

    def show_universities_statistics(self) -> NoReturn:
        data = self.__service.get_universities_statistics()

        df = pd.DataFrame(data, columns=['University', 'N of Agreements', 'Average score', 'Median score',
                                         'Top 20% score', 'Top 10% score', 'Top 5% score'])
        df = df.round(1)
        df.index += 1
        display(df)

    def show_universities_and_profiles_statistics(self) -> NoReturn:
        data = self.__service.get_profiles_statistics()

        df = pd.DataFrame(data, columns=['University', 'Profile', 'N of Agreements',
                                         'Min Score', 'Average score', 'Median score',
                                         'Top 20% score', 'Top 10% score', 'Top 5% score'])
        df = df.round(1)
        df.index += 1
        display(df)

    def show_current_applications_details_for(self, student_id: StudentId) -> NoReturn:
        data = self.__service.get_applications_details_for(student_id)

        df = pd.DataFrame(data, columns=['University', 'Profile', 'Current Position',
                                         'N of Places', 'Score', 'Min Score'])
        df.index += 1
        display(df)
