from src.core import StudentId, Student, University
from src.parsers.parser import CsvParser, FileExtension, HeadersMapping, HtmlParser

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from re import match
from typing import List, Tuple


class MtuciParser(CsvParser, HtmlParser):

    def for_university(self) -> University:
        return University.MTUCI

    def supported_file_extensions(self) -> List[FileExtension]:
        return [FileExtension.HTML, FileExtension.CSV]

    def _headers_mapping(self, file_extension: FileExtension):
        return HeadersMapping('СНИЛС/Код физ.лица', 'Сумма баллов', 'Согласие на зачисление', 'Нуждаемость в общежитии')

    def _parse_student_id(self, raw_id: str) -> StudentId:
        if match('[0-9]{3}-[0-9]{3}-[0-9]{3} [0-9]{2}', raw_id):
            return StudentId(raw_id)
        elif match('[1-9][0-9]{4}', raw_id):
            return StudentId(f"MTUCI № {raw_id}")
        else:
            raise Exception("found incompatible id", raw_id)

    def _parse_dormitory_requirement(self, raw_value: str) -> bool:
        if raw_value == 'Да':
            return True
        elif raw_value == 'Нет':
            return False
        else:
            raise Exception("found incompatible dormitory", raw_value)

    def _parse_agreement_submission(self, raw_value: str) -> bool:
        if raw_value == 'Да':
            return True
        elif raw_value == 'Нет':
            return False
        else:
            raise Exception("found incompatible agreement", raw_value)

    def _find_applications_table_data(self, data: BeautifulSoup) -> Tuple[List[str], ResultSet[Tag]]:
        table = data.find('label', attrs={'id': 'showFullTable'}).find_next_sibling('table')
        return [el.text for el in table.thead.find('tr').findAll('th', recursive=False)], table.tbody.findAll('tr')

    def _parse_student_from_html_row(self, row: Tag, positions: List[int]) -> Student:
        values = row.findAll('td', recursive=False)

        student_id = self._parse_student_id(values[positions[0]].text)
        score_text = values[positions[1]].find('b').text
        score = int(score_text) if score_text else 0
        agreement_found = self._parse_agreement_submission(values[positions[2]].text)
        dormitory_required = self._parse_dormitory_requirement(values[positions[3]].text)

        return Student(student_id, score, agreement_found)
