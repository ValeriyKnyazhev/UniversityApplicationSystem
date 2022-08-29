from src.core import StudentId, University
from src.parsers.parser import CsvParser, HeadersMapping

from colorama import Fore, Style
from re import match
from typing import Callable, Dict


class MpolitechParser(CsvParser):

    def for_university(self) -> University:
        return University.MPOLITECH

    def _headers_mapping(self) -> HeadersMapping:
        return HeadersMapping('СНИЛС/Уникальный номер', '\xa0Итоговый\xa0 балл', '\xa0Согласие\xa0о зачислении',
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
