from abc import ABCMeta, abstractmethod
from enum import Enum

from src.core import StudentId, Student, University

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from colorama import Fore, Style
import csv
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, List, TextIO, Tuple


class FileExtension(Enum):
    CSV = "csv"
    HTML = "html"

    def equals(self, value: str):
        return self.value == value


@dataclass(frozen=True)
class HeadersMapping:
    id: str
    score: str
    agreement_submitted: str
    dormitory_requirement: Optional[str] = field(default=None)


class Parser(metaclass=ABCMeta):

    def parse(self, university: University, file_path: str) -> List[Student]:
        students: List[Student] = []

        with open(file_path, 'r', encoding='utf-8-sig') as file:
            print(Fore.GREEN + f"{university} file {file_path} read started." + Style.RESET_ALL)
            file_extension: FileExtension = FileExtension(file_path.split('.')[-1])
            for parser in Parser.__subclasses__():
                if isinstance(self, parser) and file_extension in parser.supported_file_extensions(self):
                    students = parser._parse_data(self, file, file_extension)
                    break
            print(f"{len(students)} student applications uploaded from file {file_path}.")
            print(Fore.GREEN + f"{university} file {file_path} read finished." + Style.RESET_ALL)

        return students

    @abstractmethod
    def _parse_data(self, file: TextIO, extension: FileExtension) -> List[Student]:
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def for_university(self) -> University:
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def supported_file_extensions(self) -> List[FileExtension]:
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def _headers_mapping(self, file_extension: FileExtension) -> HeadersMapping:
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def _parse_student_id(self, raw_id: str) -> StudentId:
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def _parse_dormitory_requirement(self, raw_value) -> bool:
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def _parse_agreement_submission(self, raw_value) -> bool:
        raise NotImplementedError("Please Implement this method")

    def _excluding_conditions(self) -> Dict[str, Callable[[str], bool]]:
        return {}


class CsvParser(Parser, metaclass=ABCMeta):

    def _parse_data(self, file: TextIO, extension: FileExtension) -> List[Student]:
        if extension != FileExtension.CSV:
            raise Exception('Incompatible file extension')
        return self.__read_csv(file)

    def supported_file_extensions(self) -> List[FileExtension]:
        return [FileExtension.CSV]

    def _number_of_skipped_header_lines(self) -> int:
        return 0

    def _delimiter(self) -> chr:
        return ';'

    def __read_csv(self, file: TextIO) -> List[Student]:
        students: List[Student] = []

        reader = csv.reader(file, delimiter=self._delimiter())
        headers = next(reader)

        conditions_to_filter_out: Dict[int, Callable[[str], bool]] = {}
        for header_name, condition in self._excluding_conditions().items():
            condition_value_position: int = headers.index(header_name)
            conditions_to_filter_out[condition_value_position] = condition

        headers_mapping: HeadersMapping = self._headers_mapping(FileExtension.CSV)
        data_positions: List[int] = [headers.index(name) for name in [headers_mapping.id, headers_mapping.score,
                                                                      headers_mapping.agreement_submitted]]

        skip_header_lines: int = self._number_of_skipped_header_lines()
        for i in range(skip_header_lines):
            next(reader)

        line_number: int = skip_header_lines
        for row in reader:
            try:
                line_number += 1

                # filter out if any excluding condition met
                should_skip_student: bool = False
                for position, condition in conditions_to_filter_out.items():
                    if condition(row[position]):
                        should_skip_student = True

                student_id: StudentId = self._parse_student_id(row[data_positions[0]])
                score: int = int(row[data_positions[1]])
                agreement_submitted: bool = self._parse_agreement_submission(row[data_positions[2]])

                if not should_skip_student:
                    students.append(Student(student_id, score, agreement_submitted))
            except Exception as e:
                print('An exception occurred in line {}: {}'.format(line_number, str(e)))
                print('Row: {}'.format(row))

        return students


class HtmlParser(Parser, metaclass=ABCMeta):

    def _parse_data(self, file: TextIO, extension: FileExtension) -> List[Student]:
        if extension != FileExtension.HTML:
            raise Exception('Incompatible file extension')
        return self.__read_html(file)

    def supported_file_extensions(self) -> List[FileExtension]:
        return [FileExtension.HTML]

    @abstractmethod
    def _find_applications_table_data(self, data: BeautifulSoup) -> Tuple[List[str], ResultSet[Tag]]:
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def _parse_student_from_html_row(self, row: Tag, positions: List[int]) -> Student:
        raise NotImplementedError("Please Implement this method")

    def __read_html(self, file: TextIO) -> List[Student]:
        students: List[Student] = []

        data = BeautifulSoup(file.read(), 'lxml')

        general_contest: Tuple[List[str], ResultSet[Tag]] = self._find_applications_table_data(data)

        headers: List[str] = general_contest[0]
        headers_mapping: HeadersMapping = self._headers_mapping(FileExtension.HTML)
        data_positions: List[int] = [headers.index(name) for name in [headers_mapping.id,
                                                                      headers_mapping.score,
                                                                      headers_mapping.agreement_submitted,
                                                                      headers_mapping.dormitory_requirement]]

        if len(data_positions) > 4:
            raise Exception("Only 4 values can be read from table rows")

        conditions_to_filter_out: Dict[int, Callable[[str], bool]] = {}
        for header_name, condition in self._excluding_conditions().items():
            condition_value_position: int = headers.index(header_name)
            conditions_to_filter_out[condition_value_position] = condition

        line_number: int = 0
        applications_data: ResultSet[Tag] = general_contest[1]
        for application in applications_data:
            try:
                line_number += 1

                # filter out if any excluding condition met
                should_skip_student: bool = False
                for position, condition in conditions_to_filter_out.items():
                    values: List[Tag] = application.findAll('td', recursive=False)
                    if condition(values[position].text):
                        should_skip_student = True

                if not should_skip_student:
                    students.append(self._parse_student_from_html_row(application, data_positions))
            except Exception as e:
                print('An exception occurred in line {}: {}'.format(line_number, str(e)))
                print('Row: {}'.format(application))

        return students
