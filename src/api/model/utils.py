# make class have all fields equal to TrainingBase but with required = True


from typing import Type
from pydantic import BaseModel


def make_all_required(cls: Type[BaseModel]) -> Type[BaseModel]:
    """Mark all fields of the class as required"""
    for field in cls.__fields__.values():
        field.required = True
    return cls
