from src.core import StudentId, Student, University
from src.parsers.parser import CsvParser, FileExtension, HeadersMapping, HtmlParser

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from colorama import Fore, Style
from re import match
from typing import Callable, Dict, List, Tuple


class MpolitechParser(CsvParser, HtmlParser):

    def for_university(self) -> University:
        return University.MPOLITECH

    def supported_file_extensions(self) -> List[FileExtension]:
        return [FileExtension.HTML, FileExtension.CSV]

    def _headers_mapping(self, file_extension: FileExtension) -> HeadersMapping:
        if file_extension == FileExtension.CSV:
            return HeadersMapping('СНИЛС/Уникальный номер', '\xa0Итоговый\xa0 балл', '\xa0Согласие\xa0о зачислении',
                              '\xa0Общежитие\xa0')
        else:
            return HeadersMapping('СНИЛС/Уникальныйномер', '\xa0Итоговый\xa0балл', '\xa0Согласие\xa0о зачислении',
                                  '\xa0Общежитие\xa0')

    def _excluding_conditions(self) -> Dict[str, Callable[[str], bool]]:
        # common rights for applications where benefit field is equal to 0
        return {'\xa0Льгота\xa0': lambda x: int(x) != 0}

    def _parse_student_id(self, raw_id: str) -> StudentId:
        if match('[1-9][0-9]{2}-[0-9]{3}-[0-9]{3} [0-9]{2}', raw_id):
            return StudentId(raw_id)
        elif match('[1-9][0-9]{4}', raw_id):
            return StudentId(f"MPOLITECH № {raw_id}")
        else:
            raise Exception("found incompatible id", raw_id)

    def _parse_dormitory_requirement(self, raw_value: str) -> bool:
        if 'не нужд.' in raw_value:
            return False
        elif 'нужд.' in raw_value:
            return True
        else:
            raise Exception("WARNING: found incompatible dormitory", raw_value)

    def _parse_agreement_submission(self, raw_value: str) -> bool:
        if 'да (№1)' in raw_value:
            return True
        elif 'да (№2)' in raw_value:
            print(Fore.YELLOW + '{} agreement found'.format(raw_value) + Style.RESET_ALL)
            return True
        elif 'да (№3)' in raw_value:
            print(Fore.YELLOW + '{} agreement found'.format(raw_value) + Style.RESET_ALL)
            return True
        elif 'подано на' in raw_value:
            return False
        elif raw_value == "\xa0 \xa0":
            return False
        else:
            raise Exception("WARNING: found incompatible agreement", raw_value)

    def _delimiter(self):
        return ','

    def _find_applications_table_data(self, data: BeautifulSoup) -> Tuple[List[str], ResultSet[Tag]]:
        table = data.find('div', attrs={'id': 'div4'}).find('table', recursive=False).tbody
        return [el.text for el in table.find('tr').findAll('td', recursive=False)], table.findAll('tr')[1:]

    def _parse_student_from_html_row(self, row: Tag, positions: List[int]) -> Student:
        values = row.findAll('td', recursive=False)

        student_id = self._parse_student_id(values[positions[0]].text)
        score = int(values[positions[1]].text)
        agreement_found = self._parse_agreement_submission(values[positions[2]].text)
        dormitory_required = self._parse_dormitory_requirement(values[positions[3]].text)

        return Student(student_id, score, agreement_found)

    # @staticmethod
    # def __remove_specific_symbols(value: str) -> str:
    #     return value.replace('&nbsp;', '').replace('<br>', )
