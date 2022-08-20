from abc import ABC, abstractmethod
from enum import Enum

from typing import Optional, List

from dataclasses import dataclass

from src.core import StudentId, Student, University

from colorama import Fore, Style

import csv


class FileExtension(Enum):
    CSV = "csv"
    HTML = "html"

    def equals(self, value):
        return self.value == value


@dataclass(frozen=True)
class HeadersMapping:
    id: str
    score: str
    agreement_submitted: str
    dormitory_requirement: Optional[str]


class Parser(ABC):

    def parse(self, university: University, file_path: str) -> List[Student]:
        required_extension = self.supportedFileExtension()

        if not file_path.endswith("." + required_extension.value):
            raise Exception('incompatible file extension', file_path)

        if required_extension == FileExtension.CSV:
            return self.__readCsv(university, file_path)
        elif required_extension == FileExtension.HTML:
            return self._readHtml(university, file_path)
        else:
            return []

    @abstractmethod
    def forUniversity(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def supportedFileExtension(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def _headers(self) -> HeadersMapping:
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def _parseId(self, raw_id: str) -> StudentId:
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def _parseDormitory(self, raw_value):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def _parseAgreement(self, raw_value):
        raise NotImplementedError("Please Implement this method")

    def _shouldSkipAdditionalHeaderLines(self):
        return 0

    def _delimiter(self) -> chr:
        return ';'

    def _filterOutConditions(self):
        return {}

    def _readHtml(self, university: University, file_path: str) -> List[Student]:
        raise NotImplementedError("Please Implement this method")

    def __readCsv(self, university: University, file_path: str) -> List[Student]:
        students = []
        with open(file_path, encoding='utf-8') as file:
            print(Fore.GREEN + "{} file {} read started".format(university, file_path) + Style.RESET_ALL)

            reader = csv.reader(file, delimiter=self._delimiter())
            headers = next(reader)

            conditions_to_filter_out = {}
            for name, condition in self._filterOutConditions().items():
                conditionValuePosition = headers.index(name)
                conditions_to_filter_out[conditionValuePosition] = condition

            headers_mapping = self._headers()
            data_positions = [headers.index(name) for name in
                              [headers_mapping.id, headers_mapping.score, headers_mapping.agreement_submitted]]

            skip_lines = self._shouldSkipAdditionalHeaderLines()
            for i in range(skip_lines):
                next(reader)

            line_number = skip_lines

            for row in reader:
                try:
                    line_number += 1

                    # filter out if any condition met
                    should_skip_student = False
                    for position, condition in conditions_to_filter_out.items():
                        if condition(row[position]):
                            should_skip_student = True

                    student_id = self._parseId(row[data_positions[0]])
                    score = int(row[data_positions[1]])
                    agreement_submitted = self._parseAgreement(row[data_positions[2]])

                    if not should_skip_student:
                        students.append(Student(student_id, score, agreement_submitted))
                except Exception as e:
                    print('An exception occurred in line {}: {}'.format(line_number, str(e)))
                    print('Row: {}'.format(row))

            print(Fore.GREEN + "{} file {} read finished".format(university, file_path) + Style.RESET_ALL)
        return students
