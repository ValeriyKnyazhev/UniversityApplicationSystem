from src.core import StudentId, University
from src.parsers.parser import CsvParser, FileExtension, HeadersMapping

from re import match


class SPBSUParser(CsvParser):

    def for_university(self) -> University:
        return University.SPBSU

    def _headers_mapping(self, file_extension: FileExtension) -> HeadersMapping:
        return HeadersMapping('СНИЛС/Уникальный код поступающего', 'Σ общ', 'Согласие на зачисление')

    def _parse_student_id(self, raw_id: str) -> StudentId:
        if match('[1-9][0-9]{2}-[0-9]{3}-[0-9]{3} [0-9]{2}', raw_id):
            return StudentId(raw_id)
        elif match('[1-9][0-9]{6}', raw_id):
            return StudentId(f"SPBSU № {raw_id}")
        else:
            raise Exception("found incompatible id", raw_id)

    def _parse_dormitory_requirement(self, raw_value: str) -> bool:
        # not found
        return False

    def _parse_agreement_submission(self, raw_value: str) -> bool:
        if raw_value == 'Yes':
            return True
        elif raw_value == 'No':
            return False
        else:
            raise Exception("WARNING: found incompatible agreement", raw_value)

    def _number_of_skipped_header_lines(self) -> int:
        return 1

    def _delimiter(self) -> chr:
        return ','
