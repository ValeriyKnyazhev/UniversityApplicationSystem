from abc import ABC, abstractmethod
from enum import Enum

from typing import Callable, Dict, Optional, List

from dataclasses import dataclass, field

from src.core import StudentId, Student, University

from colorama import Fore, Style

import csv


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


class Parser(ABC):

    def parse(self, university: University, file_path: str) -> List[Student]:
        required_extension: FileExtension = self.supported_file_extension()

        if not file_path.endswith("." + required_extension.value):
            raise Exception('incompatible file extension', file_path)

        if required_extension == FileExtension.CSV:
            return self.__read_csv(university, file_path)
        elif required_extension == FileExtension.HTML:
            return self._read_html(university, file_path)
        else:
            return []

    @abstractmethod
    def for_university(self) -> University:
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def supported_file_extension(self) -> FileExtension:
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def _headers_mapping(self) -> HeadersMapping:
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

    def _number_of_skipped_header_lines(self) -> int:
        return 0

    def _delimiter(self) -> chr:
        return ';'

    def _excluding_conditions(self) -> Dict[str, Callable[[str], bool]]:
        return {}

    def _read_html(self, university: University, file_path: str) -> List[Student]:
        raise NotImplementedError("Please Implement this method")

    def __read_csv(self, university: University, file_path: str) -> List[Student]:
        students: List[Student] = []
        with open(file_path, encoding='utf-8') as file:
            print(Fore.GREEN + f"{university} file {file_path} read started" + Style.RESET_ALL)

            reader = csv.reader(file, delimiter=self._delimiter())
            headers = next(reader)

            conditions_to_filter_out: Dict[int, Callable[[str], bool]] = {}
            for header_name, condition in self._excluding_conditions().items():
                condition_value_position: int = headers.index(header_name)
                conditions_to_filter_out[condition_value_position] = condition

            headers_mapping: HeadersMapping = self._headers_mapping()
            data_positions: List[int] = [headers.index(name) for name in [headers_mapping.id, headers_mapping.score,
                                                                          headers_mapping.agreement_submitted]]

            skip_header_lines: int = self._number_of_skipped_header_lines()
            for i in range(skip_header_lines):
                next(reader)

            line_number: int = skip_header_lines

            for row in reader:
                try:
                    line_number += 1

                    # filter out if any condition met
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

            print(Fore.GREEN + f"{university} file {file_path} read finished" + Style.RESET_ALL)
        return students
