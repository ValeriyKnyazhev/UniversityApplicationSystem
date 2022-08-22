from src.core import StudentId, University
from src.parsers.parser import FileExtension, HeadersMapping, Parser

from re import match


class MireaParser(Parser):

    def for_university(self) -> University:
        return University.MIREA

    def supported_file_extension(self) -> FileExtension:
        return FileExtension.CSV

    def _headers_mapping(self) -> HeadersMapping:
        return HeadersMapping('СНИЛС/уникальный номер', 'Сумма баллов', 'Согласие на зачисление', 'Потребность в\xa0общежитии')

    def _parse_student_id(self, raw_id) -> StudentId:
        if match('[1-9][0-9]{2}-[0-9]{3}-[0-9]{3}-[0-9]{2}', raw_id):
            parts = raw_id.split('-')
            return StudentId(f"{parts[0]}-{parts[1]}-{parts[2]} {parts[3]}")
        elif match('[1-9][0-9]{2}-[0-9]{3}-[0-9]{3} [0-9]{2}', raw_id):
            return StudentId(raw_id)
        elif match('[1-9][0-9]{6}', raw_id):
            return StudentId(f"MIREA № {raw_id}")
        else:
            raise Exception("found incompatible id", raw_id)

    def _parse_dormitory_requirement(self, raw_value) -> bool:
        if raw_value == 'требуется':
            return True
        elif raw_value in ('не требуется', 'требуется,\xa0отказано'):
            return False
        else:
            raise Exception("WARNING: found incompatible dormitory", raw_value)

    def _parse_agreement_submission(self, raw_value) -> bool:
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
