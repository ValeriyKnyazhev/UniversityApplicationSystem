from src.core.student import StudentId, Student
from src.core.university import University

from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json, LetterCase

from typing import Optional


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(eq=True, order=True, frozen=True)
class Profile(object):
    id: str = field(compare=True)
    sub_field: Optional[str] = field(compare=True, default=None, metadata=config(exclude=lambda v: v is None))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.id if self.sub_field is None else f"{self.id}:{self.sub_field}"
