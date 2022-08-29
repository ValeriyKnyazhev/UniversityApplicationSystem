from os import listdir
from os.path import isdir, isfile, join, abspath

from src.core import Profile, StudentId, Student, University
from src.parsers import Parser
from src.application.application_system import ApplicationSystem

from typing import Dict, List, Tuple

from colorama import Fore, Style

import csv


class DataLoader:

    def __init__(self):
        self.__parsers = {}
        for parserClass in Parser.__subclasses__():
            parser = parserClass()
            self.__register_parser(parser)

    def load_data(self, system: ApplicationSystem, dir_path: str):
        if not isdir(dir_path):
            raise Exception(f"Files directory should be provided, but {dir_path} found")

        files: List[str] = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
        for file in files:
            if file == 'ALREADY_LISTED.csv':
                listed_students: Dict[StudentId, Tuple[University, str]] = DataLoader.__load_listed_students(
                    abspath(join(dir_path, file))
                )
                system.add_listed_students(listed_students)
                continue

            extension: str = file.split(".")[-1]
            file_parts: List[str] = file.split('_')
            university: University = University[file_parts[0]]

            if university not in self.__parsers:
                print(Fore.RED + f"Unsupported university {university} found: file {file}" + Style.RESET_ALL)
                break

            parser: Parser = self.__parsers[university]

            if not parser.supported_file_extension().equals(extension):
                print(
                    Fore.YELLOW + f"Unsupported extension {extension} for {university} found: file {file}" + Style.RESET_ALL)
                continue

            profile: Profile = Profile(file_parts[1][: file_parts[1].index("." + extension)]) \
                if len(file_parts) == 2 \
                else Profile(file_parts[1], file_parts[2][: file_parts[2].index("." + extension)])

            students: List[Student] = parser.parse(abspath(join(dir_path, file)))
            system.add_profile_students_data(university, profile, students)

            # break line between files
            print()

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
