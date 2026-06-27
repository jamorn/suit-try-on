# config.py
from dataclasses import dataclass
from typing import Literal

@dataclass(slots=True)
class SuitConfig:
    path: str
    order: int
    sex: Literal['M', 'F']
    enabled: bool = True
    anchor_y: float = 0.2      # จุดไหล่ในรูป (0.0=บนสุด, 1.0=ล่างสุด)
    is_full_body: bool = False  # True=เดรส/ชุดยาว; scale auto-fit ให้เต็มจอ


SUIT_DATA: tuple[SuitConfig, ...] = (
    SuitConfig(path='assets/male_suit_1.png', order=1, sex='M'),
    SuitConfig(path='assets/male_suit_2.png', order=2, sex='M', anchor_y=0.25),
    SuitConfig(path='assets/female_suit_1.png', order=1, sex='F', anchor_y=0.15, is_full_body=True),
    SuitConfig(path='assets/female_suit_2.png', order=2, sex='F', anchor_y=0.15, is_full_body=True),
)

MODEL_PATH = 'assets/pose_landmarker_lite.task'
DEFAULT_SEX: Literal['M', 'F'] = 'M'