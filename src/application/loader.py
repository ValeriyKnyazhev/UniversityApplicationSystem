from os import listdir
from os.path import isdir, isfile, join, abspath

from src.core import University
from src.parsers import Parser
from src.application.application_system import ApplicationSystem

from colorama import Fore, Style


class DataLoader:

    def __init__(self):
        self.__parsers = {}
        for parserClass in Parser.__subclasses__():
            parser = parserClass()
            self.__register_parser(parser)

    def load_data(self, system: ApplicationSystem, dir_path: str):
        isdir(dir_path)
        files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
        for file in files:
            if file == 'ALREADY_LISTED.csv':
                continue

            extension = file.split(".")[-1]
            file_parts = file.split('_')
            university = University[file_parts[0]]

            if university not in self.__parsers:
                print(Fore.RED + 'Unsupported university {} found: file {}'.format(university, file) + Style.RESET_ALL)
                break

            parser = self.__parsers[university]

            if not parser.supportedFileExtension().equals(extension):
                raise Exception('Unsupported extension {} for {}'.format(extension, university))

            profile = file_parts[1][: file_parts[1].index("." + extension)]

            students = parser.parse(university, profile, abspath(join(dir_path, file)))
            system.add_profile_students_data(university, profile, students)

            # break line between files
            # print()

    def __register_parser(self, parser):
        university = parser.forUniversity()
        self.__parsers[university] = parser
