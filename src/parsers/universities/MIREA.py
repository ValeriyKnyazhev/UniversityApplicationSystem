from src.core import StudentId, Student, University
from src.parsers.parser import CsvParser, FileExtension, HtmlParser, HeadersMapping

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from re import match
from typing import List, TextIO, Tuple


class MireaParser(CsvParser, HtmlParser):

    def for_university(self) -> University:
        return University.MIREA

    def supported_file_extensions(self) -> List[FileExtension]:
        return [FileExtension.HTML, FileExtension.CSV]

    def _headers_mapping(self, file_extension: FileExtension) -> HeadersMapping:
        return HeadersMapping('СНИЛС/уникальный номер', 'Сумма баллов', 'Согласие на зачисление',
                              'Потребность в\xa0общежитии')

    def _parse_student_id(self, raw_id: str) -> StudentId:
        if match('[1-9][0-9]{2}-[0-9]{3}-[0-9]{3}-[0-9]{2}', raw_id):
            parts = raw_id.split('-')
            return StudentId(f"{parts[0]}-{parts[1]}-{parts[2]} {parts[3]}")
        elif match('[1-9][0-9]{2}-[0-9]{3}-[0-9]{3} [0-9]{2}', raw_id):
            return StudentId(raw_id)
        elif match('[1-9][0-9]{6}', raw_id):
            return StudentId(f"MIREA № {raw_id}")
        else:
            raise Exception("found incompatible id", raw_id)

    def _parse_dormitory_requirement(self, raw_value: str) -> bool:
        if raw_value == 'требуется':
            return True
        elif raw_value in ('не требуется', 'требуется, отказано'):
            return False
        else:
            raise Exception("WARNING: found incompatible dormitory", raw_value)

    def _parse_agreement_submission(self, raw_value: str) -> bool:
        if raw_value == 'да':
            return True
        elif raw_value == 'нет':
            return False
        else:
            raise Exception("WARNING: found incompatible agreement", raw_value)

    def _number_of_skipped_header_lines(self) -> int:
        return 1

    def _delimiter(self) -> chr:
        return ','

    def _find_applications_table_data(self, data: BeautifulSoup) -> Tuple[List[str], ResultSet[Tag]]:
        table = data.find('table', attrs={'class': 'namesTable'})
        return [el.text for el in table.thead.find('tr').findAll('td', recursive=False)], table.tbody.findAll('tr')

    def _parse_student_from_html_row(self, row: Tag, positions: List[int]) -> Student:
        values = row.findAll('td', recursive=False)

        student_id = self._parse_student_id(values[positions[0]].text)
        score = int(values[positions[1]].text)
        agreement_found = self._parse_agreement_submission(values[positions[2]].text)
        dormitory_required = self._parse_dormitory_requirement(values[positions[3]].text)

        return Student(student_id, score, agreement_found)
