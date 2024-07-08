from __future__ import annotations

import re
from argparse import ArgumentParser
from argparse import Namespace
from dataclasses import dataclass


AKW_TYPE = tuple[list[str], dict]


def akw(*args, **kwargs) -> AKW_TYPE:
    return (list(args), kwargs)


def fl_akw(*args, **kwargs) -> AKW_TYPE:
    kwargs["type"] = float
    kwargs["metavar"] = "LENGTH"
    kwargs["default"] = 0
    return (list(args), kwargs)


def akw_to_attr(akw: AKW_TYPE) -> str:
    string = akw[0][0]
    string = re.sub(r"^--", r"", string)
    string = re.sub(r"-", r"_", string)
    return string


@dataclass(frozen=True)
class Argumentable:
    parsed_arguments: Namespace | None

    @classmethod
    def dimension_arguments(cls) -> list[AKW_TYPE]:
        return []

    @classmethod
    def feature_arguments(cls) -> list[AKW_TYPE]:
        return []

    @classmethod
    def object_init_args(cls) -> list[str]:
        keys = set[str]()

        keys.update([akw_to_attr(arg) for arg in cls.dimension_arguments()])
        keys.update([akw_to_attr(arg) for arg in cls.feature_arguments()])
        return list(keys)

    @classmethod
    def __dimension_arguments(cls, parser: ArgumentParser):
        grp = parser.add_argument_group("Dimensions")
        for args, kwargs in cls.dimension_arguments():
            grp.add_argument(*args, **kwargs)

    @classmethod
    def __feature_arguments(cls, parser: ArgumentParser):
        grp = parser.add_argument_group("Features")
        for args, kwargs in cls.feature_arguments():
            grp.add_argument(*args, **kwargs)

    @classmethod
    def add_arguments(cls, parser: ArgumentParser):
        cls.__dimension_arguments(parser)
        cls.__feature_arguments(parser)

    @classmethod
    def from_args(
        cls,
        *,
        dimension_scale: float,
        parsed_arguments: Namespace | None = None,
        **default_kwargs,
    ):
        kwargs = default_kwargs
        for key, value in parsed_arguments.__dict__.items():
            if key not in kwargs:
                if key in cls.object_init_args():
                    kwargs[key] = value
                    if key in [
                        akw_to_attr(a) for a in cls.dimension_arguments()
                    ]:
                        kwargs[key] *= dimension_scale
        return cls(parsed_arguments=parsed_arguments, **kwargs)
