from src.core import StudentId, Student, University
from src.parsers.parser import CsvParser, FileExtension, HeadersMapping, HtmlParser

from bs4 import BeautifulSoup, ResultSet, Tag
from typing import Tuple, List


class MpeiParser(CsvParser, HtmlParser):

    def for_university(self) -> University:
        return University.MPEI

    def supported_file_extensions(self) -> List[FileExtension]:
        return [FileExtension.HTML, FileExtension.CSV]

    def _headers_mapping(self, file_extension: FileExtension) -> HeadersMapping:
        return HeadersMapping('СНИЛС или Рег.номер', 'Сумма', 'Согласие', 'Общ.')

    def _parse_student_id(self, raw_id: str) -> StudentId:
        if raw_id.startswith('СНИЛС: '):
            extracted_id = raw_id[7:]
            return StudentId(f"{extracted_id[:3]}-{extracted_id[3:6]}-{extracted_id[6:9]} {extracted_id[9:]}")
        elif raw_id.startswith('Рег.номер: '):
            return StudentId(f"MPEI № {raw_id[11:]}")
        else:
            raise Exception("found incompatible id", raw_id)

    def _parse_dormitory_requirement(self, raw_value: str) -> bool:
        if raw_value == 'с/о':
            return True
        elif raw_value == 'б/о':
            return False
        else:
            raise Exception("WARNING: found incompatible dormitory", raw_value)

    def _parse_agreement_submission(self, raw_value: str) -> bool:
        if raw_value == 'подано':
            return True
        elif raw_value == 'не подано':
            return False
        else:
            raise Exception("WARNING: found incompatible agreement", raw_value)

    def _number_of_skipped_header_lines(self) -> int:
        return 1

    def _delimiter(self) -> chr:
        return ','

    def _find_applications_table_data(self, data: BeautifulSoup) -> Tuple[List[str], ResultSet[Tag]]:
        table: Tag = data.find('div', attrs={'id': 'd2103', 'class': 'c2101c'}).find('table', recursive=False).tbody
        main_headers: Tag = table.find('tr', recursive=False)

        headers: List[str] = []
        for header_column in main_headers.findAll('td', recursive=False):
            if header_column.text == 'Баллы*':
                headers.extend([el.text for el in main_headers.find_next_sibling().findAll('td', recursive=False)])
            else:
                headers.append(header_column.text)
        return headers, table.find_all('tr', recursive=False)[1:]

    def _parse_student_from_html_row(self, row: Tag, positions: List[int]) -> Student:
        values = row.find_all('td', recursive=False)
        print(values)

        student_id = self._parse_student_id(values[positions[0]].text)
        score = int(values[positions[1]].text)
        agreement_found = self._parse_agreement_submission(values[positions[2]].text)
        dormitory_required = self._parse_dormitory_requirement(values[positions[3]].text)

        return Student(student_id, score, agreement_found)
