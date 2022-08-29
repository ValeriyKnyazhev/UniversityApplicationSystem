from src.core import StudentId, University
from src.parsers.parser import CsvParser, HeadersMapping


class MpeiParser(CsvParser):

    def for_university(self) -> University:
        return University.MPEI

    def _headers_mapping(self) -> HeadersMapping:
        return HeadersMapping('СНИЛС или Рег.номер', '\ufeffСумма', 'Согласие', 'Общ.')

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
