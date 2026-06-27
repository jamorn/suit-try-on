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
    x_offset: int = 0           # ✨ เพิ่มใหม่: เลื่อนซ้าย/ขวา (px) — ค่าบวก=ขวา, ค่าลบ=ซ้าย


SUIT_DATA: tuple[SuitConfig, ...] = (
    # ชุดผู้ชาย: เลื่อนไปทางขวา +15px เพื่อชดเชยที่ชุดเอียงซ้าย
    SuitConfig(path='assets/male_suit_1.png', order=1, sex='M', 
               anchor_y=0.28, scale_factor=1.5, x_offset=5),
    SuitConfig(path='assets/male_suit_2.png', order=2, sex='M', 
               anchor_y=0.30, scale_factor=1.5, x_offset=5),
    
    # ชุดผู้หญิง (ไม่เลื่อน)
    SuitConfig(path='assets/female_suit_1.png', order=1, sex='F', 
               anchor_y=0.12, scale_factor=1.6, is_full_body=True),
    SuitConfig(path='assets/female_suit_2.png', order=2, sex='F', 
               anchor_y=0.10, scale_factor=1.7, is_full_body=True),
)

MODEL_PATH = 'assets/pose_landmarker_lite.task'
DEFAULT_SEX: Literal['M', 'F'] = 'M'