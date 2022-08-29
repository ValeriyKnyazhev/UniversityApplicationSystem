from os import listdir
from os.path import isdir, isfile, join, abspath
import inspect

from src.core import Profile, StudentId, Student, University
from src.parsers import Parser
from src.application.application_system import ApplicationSystem

from colorama import Fore, Style
import csv
from typing import Dict, List, Tuple


class DataLoader:

    def __init__(self):
        self.__parsers = {}
        for parserClass in self.__all_subclasses(Parser):
            if not inspect.isabstract(parserClass):
                parser = parserClass()
                self.__register_parser(parser)

    def load_data(self, system: ApplicationSystem, dir_path: str):
        if not isdir(dir_path):
            raise Exception(f"Files directory should be provided, but {dir_path} found")

        files: List[str] = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

        if 'ALREADY_LISTED.csv' in files:
            listed_students: Dict[StudentId, Tuple[University, str]] = DataLoader.__load_listed_students(
                abspath(join(dir_path, 'ALREADY_LISTED.csv'))
            )
            system.add_listed_students(listed_students)

        for university in University:
            if university not in self.__parsers:
                continue

            parser: Parser = self.__parsers[university]
            for file_extension in parser.supported_file_extensions():
                for file in [f for f in files if f.startswith(university.name) and f.endswith(file_extension.value)]:
                    file_parts: List[str] = file.split('_')
                    profile: Profile = Profile(file_parts[1][: file_parts[1].index("." + file_extension.value)]) \
                        if len(file_parts) == 2 \
                        else Profile(file_parts[1], file_parts[2][: file_parts[2].index("." + file_extension.value)])

                    if system.is_profile_application_uploaded(university, profile):
                        print(
                            Fore.YELLOW + f"Students for {profile} in {university} already uploaded: skipping file {file}" + Style.RESET_ALL)
                    else:
                        students: List[Student] = parser.parse(university, abspath(join(dir_path, file)))
                        system.add_profile_students_data(university, profile, students)

                    # break line between files
                    print()

    def __all_subclasses(self, cls):
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in self.__all_subclasses(c)])

    def __register_parser(self, parser: Parser):
        university: University = parser.for_university()
        self.__parsers[university] = parser
        print(f"Parser for {university} registered.")

    @staticmethod
    def __load_listed_students(file_path: str) -> Dict[StudentId, Tuple[University, str]]:
        listed_students: Dict[StudentId, Tuple[University, str]] = {}
        with open(file_path, encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            headers = next(reader)

            data_positions = [headers.index(name) for name in ['\ufeffUniversity', 'StudentId', 'Reason']]

            line_number: int = 0

            for row in reader:
                try:
                    line_number += 1

                    university: University = University[row[data_positions[0]]]
                    student_id: StudentId = StudentId(row[data_positions[1]])
                    reason: str = row[data_positions[2]]

                    listed_students[student_id]: Tuple[University, str] = (university, reason)
                except Exception as e:
                    print(f"An exception occurred in line {line_number}: {str(e)}")
                    print(f"Row: {row}")

        print(f"{len(listed_students)} already listed students uploaded")
        return listed_students
