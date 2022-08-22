from src.core import StudentId, University
from src.parsers.parser import FileExtension, HeadersMapping, Parser

from re import match


class MiptParser(Parser):

    def for_university(self) -> University:
        return University.MIPT

    def supported_file_extension(self) -> FileExtension:
        return FileExtension.CSV

    def _headers_mapping(self) -> HeadersMapping:
        return HeadersMapping('СНИЛС / ИНД №', 'С-ма с ИД', 'СЗ', 'Общежитие')

    def _parse_student_id(self, raw_id: str) -> StudentId:
        if match('[1-9][0-9]{2}-[0-9]{3}-[0-9]{3} [0-9]{2}', raw_id):
            return StudentId(raw_id)
        elif match('[1-9][0-9]{4}', raw_id):
            return StudentId(f"MTUCI № {raw_id}")
        else:
            raise Exception("found incompatible id", raw_id)

    def _parse_dormitory_requirement(self, raw_value: str) -> bool:
        if raw_value == 'Yes':
            return True
        elif raw_value == 'No':
            return False
        else:
            raise Exception("WARNING: found incompatible dormitory", raw_value)

    def _parse_agreement_submission(self, raw_value: str) -> bool:
        if raw_value == 'Yes':
            return True
        elif raw_value == 'No':
            return False
        else:
            raise Exception("WARNING: found incompatible agreement", raw_value)

    def _delimiter(self) -> chr:
        return ','
