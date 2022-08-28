from src.core import StudentId, Student, University
from src.parsers.parser import FileExtension, HeadersMapping, Parser

from re import match
from typing import List, Tuple
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag


class MietParser(Parser):

    def for_university(self) -> University:
        return University.MIET

    def supported_file_extension(self) -> FileExtension:
        return FileExtension.HTML

    def _headers_mapping(self) -> HeadersMapping:
        return HeadersMapping('Рег. Номер', 'Сумма', 'Согласие', 'Общежитие')

    def _parse_student_id(self, raw_id: str) -> StudentId:
        if match('[0-9]{3}-[0-9]{3}-[0-9]{3} [0-9]{2}', raw_id):
            return StudentId(raw_id)
        elif match('[1-9][0-9]{4}', raw_id):
            return StudentId(f"MIET № {raw_id}")
        else:
            raise Exception("found incompatible id", raw_id)

    def _parse_dormitory_requirement(self, raw_value: str) -> bool:
        if raw_value == '+':
            return True
        elif raw_value == '':
            return False
        else:
            raise Exception("WARNING: found incompatible dormitory", raw_value)

    def _parse_agreement_submission(self, raw_value: str) -> bool:
        if raw_value == '+':
            return True
        elif raw_value == '':
            return False
        else:
            raise Exception("WARNING: found incompatible agreement", raw_value)

    def _number_of_skipped_header_lines(self) -> int:
        return 1

    def _find_applications_table_data(self, data: BeautifulSoup) -> Tuple[Tag, ResultSet[Tag]]:
        table = data.find('table', attrs={'id': 'dataTable'})
        return table.thead.find('tr'), table.tbody.findAll('tr')

    def _parse_student_from_html_row(self, row: Tag, positions: List[int]):
        values = row.findAll('td', recursive=False)
        if len(positions) > 4:
            raise Exception("Only 4 values can be read from table rows")

        student_id = self._parse_student_id(values[positions[0]].text)
        score = int(values[positions[1]].text)
        agreement_found = self._parse_agreement_submission(values[positions[2]].text)
        dormitory_required = self._parse_dormitory_requirement(values[positions[3]].text)

        return Student(student_id, score, agreement_found)

