# config.py
from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class SuitConfig:
    path: str
    order: int
    sex: Literal['M', 'F']
    enabled: bool = True
    anchor_y: float = 0.2       # จุดไหล่ในรูป (0.0=บนสุด, 1.0=ล่างสุด)
    scale_factor: float = 1.5   # สเกลความกว้างเฉพาะตัวชุด
    is_full_body: bool = False  # True=เดรส/ชุดยาว
    x_offset: int = 0           # เลื่อนซ้าย/ขวา (px) — ค่าบวก=ขวา, ค่าลบ=ซ้าย
    y_offset: int = 0           # ✨ เพิ่มใหม่: เลื่อนขึ้น/ลง (px) — ค่าบวก=ลง, ค่าลบ=ขึ้น
    stretch_x: float = 1.0      # ยืด/หดแกนกว้าง (1.0=ปกติ)
    stretch_y: float = 1.0      # ยืด/หดแกนสูง (1.0=ปกติ)


SUIT_DATA: tuple[SuitConfig, ...] = (
    # ชุดผู้ชาย
    SuitConfig(path='assets/male_suit_1.png', order=1, sex='M',
               anchor_y=0.28, scale_factor=1.5, x_offset=5, y_offset=0,
               stretch_x=1.0, stretch_y=1.0),
    SuitConfig(path='assets/male_suit_2.png', order=2, sex='M',
               anchor_y=0.30, scale_factor=1.5, x_offset=5, y_offset=0,
               stretch_x=1.0, stretch_y=1.0),

    # ชุดผู้หญิง
    SuitConfig(path='assets/female_suit_1.png', order=1, sex='F',
               anchor_y=0.12, scale_factor=1.6, is_full_body=True,
               stretch_x=1.0, stretch_y=1.0),
    SuitConfig(path='assets/female_suit_2.png', order=2, sex='F',
               anchor_y=0.10, scale_factor=1.7, is_full_body=True,
               stretch_x=1.0, stretch_y=1.0),
)

MODEL_PATH = 'assets/pose_landmarker_lite.task'
DEFAULT_SEX: Literal['M', 'F'] = 'M'