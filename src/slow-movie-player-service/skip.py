import dataclasses
import abc
from typing import Union


@dataclasses.dataclass(frozen=True)
class AbstractSkip(abc.ABC):
    amount: Union[int, float]

    def __new__(cls, *args, **kwargs):
        if cls.__bases__[0] == abc.ABC:
            raise TypeError("Cannot instantiate abstract class.")

        return super().__new__(cls)

    def __post_init__(self):
        for field_name, required_type in self.__annotations__.items():
            provided_type = self.__dict__[field_name]

            if not isinstance(provided_type, required_type):
                raise TypeError(
                    "Field '{}' is of type '{}', but should be of type '{}' instead.".format(
                        field_name,
                        type(provided_type),
                        required_type
                    )
                )


@dataclasses.dataclass(frozen=True)
class FrameSkip(AbstractSkip):
    amount: int


@dataclasses.dataclass(frozen=True)
class TimeSkip(AbstractSkip):
    amount: float
