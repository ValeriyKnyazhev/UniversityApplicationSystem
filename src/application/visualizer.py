from enum import Enum

from src.core import Profile, StudentId, University
from src.application import ApplicationService

from typing import Dict, List, NoReturn, Tuple

import sys
import pandas as pd
import pdfkit
from IPython.display import display
from jinja2 import Environment, FileSystemLoader, PackageLoader
from time import localtime, strftime

pd.set_option("display.max_rows", None)
pd.set_option("display.precision", 2)


class ReportType(Enum):
    BRIEF = "brief"
    FULL = "full"


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

        df = self.__build_dataframe(data, ['Id', 'Score', "Chosen University", "Chosen Profile"])
        display(df)

    def show_all_students_and_chosen_profile_where_score_ge_and_admission_possible(self,
                                                                                   university: University,
                                                                                   profile: Profile,
                                                                                   score: int) -> NoReturn:
        data = self.__service.get_all_students_with_chosen_profile_where_score_ge_and_admission_possible(
            university, profile, score
        )

        df = self.__build_dataframe(data, ['Id', 'Score', f"Chosen Profile in {university}"])
        display(df)

    def show_agreements_distribution(self) -> NoReturn:
        data = [(university, n_agreements) for university, n_agreements
                in self.__service.get_number_of_agreements_by_university().items()]

        df = self.__build_dataframe(data, ['University', 'Agreements'])
        display(df)

    def show_pending_agreements_distribution(self) -> NoReturn:
        data = [(university, n_agreements) for university, n_agreements
                in self.__service.get_number_of_pending_agreements_by_university().items()]

        df = self.__build_dataframe(data, ['University', 'Agreements'])
        display(df)

    def show_universities_statistics(self) -> NoReturn:
        data = self.__service.get_universities_statistics()

        df = self.__build_dataframe(data, ['University', 'N of Agreements', 'N of Places', 'Average score',
                                           'Median score', 'Top 20% score', 'Top 10% score', 'Top 5% score'])
        display(df)

    def show_universities_and_profiles_statistics(self) -> NoReturn:
        data = self.__service.get_profiles_statistics()

        df = self.__build_dataframe(data, ['University', 'Profile', 'N of Agreements', 'N of Places',
                                           'Min Score', 'Average score', 'Median score',
                                           'Top 20% score', 'Top 10% score', 'Top 5% score'])
        display(df)

    def show_current_applications_details_for(self, student_id: StudentId) -> NoReturn:
        data = self.__service.get_applications_details_for(student_id)
        df = self.__build_dataframe(data, ['University', 'Profile', 'Current Position',
                                           'N of Places', 'Score', 'Min Score'])
        display(df)

    def get_report_for(self, student_id: StudentId, report_type: ReportType = ReportType.BRIEF) -> NoReturn:
        applications_details = self.__service.get_applications_details_for(student_id)
        universities_details = self.__service.get_universities_statistics()
        profiles_details = self.__service.get_profiles_statistics()
        students_lists = self.__fetch_students_lists(applications_details) if report_type == ReportType.FULL else {}

        env = Environment(loader=PackageLoader('src.application', 'report'))
        template = env.get_template(report_type.value + '_report_template.html')
        pdf_data = template.render(
            id=student_id.id,
            generated_at=strftime("%d/%b/%Y %H:%M:%S", localtime()),
            applications_details=applications_details,
            universities_details=universities_details,
            profiles_details=profiles_details,
            students_lists=students_lists
        )

        cssPath = 'src/application/report/report_template.css'
        reportFileName = f"student_{student_id.id.replace(' ', '-')}_{report_type.value}.pdf"

        if sys.platform.startswith('win'):
            path_wkthmltopdf = b'C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe'
            config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
            pdfkit.from_string(pdf_data, reportFileName, css=cssPath, configuration=config)
        else:
            pdfkit.from_string(pdf_data, reportFileName, css=cssPath)

    def __build_dataframe(self, data: List[Tuple], headers: List[str]) -> pd.DataFrame:
        dataframe = pd.DataFrame(data, columns=headers)
        dataframe.index += 1
        return dataframe

    def __fetch_students_lists(self, applications: List[Tuple[University, Profile, int, int, int, int]]) -> \
            Dict[Tuple[University, Profile], List[Tuple[StudentId, int, Profile]]]:
        lists = {}
        for application in applications:
            university: University = application[0]
            profile: Profile = application[1]
            students = self.__service.get_all_students_with_chosen_profile_where_score_ge_and_admission_possible(
                university, profile, score=application[4]
            )
            lists[(university, profile)] = students
        return lists
