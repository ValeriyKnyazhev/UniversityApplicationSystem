from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json, LetterCase

from typing import Optional


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(eq=True, order=True, frozen=True)
class StudentId(object):
    id: str = field(compare=True)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.id


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(eq=True, order=True)
class Student:
    id: StudentId
    score: int
    agreement_submitted: bool
    dormitory_requirement: Optional[bool] = field(default=None, metadata=config(exclude=lambda v: v is None))

    # def __init__(self, _id: StudentId, score: int, agreement_submitted: bool):
    #     self.id = _id
    #     self.score = score
    #     self.agreement_submitted = agreement_submitted

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.to_json()
