# config.py
SUIT_DATA = [
    {
        'path': 'assets/male_suit_1.png',
        'order': 1,
        'sex': 'M',
        'status': True,
        'y_offset': 0.25  # ปรับค่านี้เพื่อขยับตำแหน่งแนวตั้ง (ค่าที่แนะนำ 0.2 - 0.4)
    },
    {
        'path': 'assets/male_suit_2.png',
        'order': 2,
        'sex': 'M',
        'status': True,
        'y_offset': 0.28
    },
    {
        'path': 'assets/female_suit_1.png',
        'order': 1,
        'sex': 'F',
        'status': True,
        'y_offset': 0.22
    },
    {
        'path': 'assets/female_suit_2.png',
        'order': 2,
        'sex': 'F',
        'status': True,
        'y_offset': 0.24
    }
]

MODEL_PATH = 'assets/pose_landmarker_lite.task'
DEFAULT_SEX = 'M'