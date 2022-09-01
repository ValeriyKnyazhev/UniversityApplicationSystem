from src.core import StudentId, Student, University
from src.parsers.parser import FileExtension, HeadersMapping, HtmlParser

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from re import match
from typing import List, Tuple


class MaiParser(HtmlParser):

    def for_university(self) -> University:
        return University.MAI

    def _headers_mapping(self, file_extension: FileExtension) -> HeadersMapping:
        return HeadersMapping('СНИЛС/УКП', 'Сумма конкурсных баллов', 'Согласие на\xa0зачисление',
                              'Нуждаемость в\xa0общежитии')

    def _parse_student_id(self, raw_id: str) -> StudentId:
        if match('[1-9][0-9]{2}-[0-9]{3}-[0-9]{3} [0-9]{2}', raw_id):
            return StudentId(raw_id)
        elif match('[0-9]{9}', raw_id):
            return StudentId(f"MAI № {raw_id}")
        else:
            raise Exception("found incompatible id", raw_id)

    def _parse_dormitory_requirement(self, raw_value: str) -> bool:
        if raw_value == '✓':
            return True
        elif raw_value == 'No':
            return False
        else:
            raise Exception("found incompatible dormitory", raw_value)

    def _parse_agreement_submission(self, raw_value: str) -> bool:
        if raw_value == '✓':
            return True
        elif raw_value == 'No':
            return False
        else:
            raise Exception("found incompatible agreement", raw_value)

    def _find_applications_table_data(self, data: BeautifulSoup) -> Tuple[List[str], ResultSet[Tag]]:
        tables = data.find('div', attrs={'id': 'tab'})
        should_use_next = False
        for child in tables.findChildren():
            if should_use_next:
                return [el.text for el in child.tbody.find('tr', recursive=False).findAll('th', recursive=False)],\
                       child.tbody.findAll('tr', recursive=False)[1:]
            if child.text == 'Лица, поступающие по общему конкурсу':
                should_use_next = True
        raise Exception("WARNING: incorrect data structure")

    def _parse_student_from_html_row(self, row: Tag, positions: List[int]) -> Student:
        values = row.findAll('td', recursive=False)

        student_id = self._parse_student_id(values[positions[0]].nobr.text)
        score = int(values[positions[1]].text)
        agreement_found = self._parse_agreement_submission(
            values[positions[2]].span.text if values[positions[2]].find('span') else 'No')
        dormitory_required = self._parse_dormitory_requirement(
            values[positions[3]].span.text if values[positions[3]].find('span') else 'No')

        return Student(student_id, score, agreement_found)
