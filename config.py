from dataclasses import dataclass


@dataclass(slots=True)
class SuitConfig:
    path: str
    order: int
    sex: str
    enabled: bool = True
    y_offset: float = 0.25


SUIT_DATA: list[SuitConfig] = [
    SuitConfig(
        path='assets/male_suit_1.png',
        order=1,
        sex='M',
        enabled=True,
        y_offset=0.25,
    ),
    SuitConfig(
        path='assets/male_suit_2.png',
        order=2,
        sex='M',
        enabled=True,
        y_offset=0.28,
    ),
    SuitConfig(
        path='assets/female_suit_1.png',
        order=1,
        sex='F',
        enabled=True,
        y_offset=0.22,
    ),
    SuitConfig(
        path='assets/female_suit_2.png',
        order=2,
        sex='F',
        enabled=True,
        y_offset=0.24,
    ),
]

MODEL_PATH = 'assets/pose_landmarker_lite.task'
DEFAULT_SEX = 'M'