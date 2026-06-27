# 👔 Virtual Suit Try-On

โปรแกรมลองเสื้อผ้าเสมือนจริงแบบ real-time ด้วย **MediaPipe PoseLandmarker** + **OpenCV**

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ ฟีเจอร์

- ✅ **ตรวจจับร่างกายแบบ real-time** — MediaPipe PoseLandmarker (VIDEO mode)
- ✅ **รองรับชุดหลายแบบ** — แยกชุดชาย/หญิง สลับได้ทันที
- ✅ **ปรับตำแหน่งชุด** — X/Y offset (เลื่อนซ้าย/ขวา/ขึ้น/ลง)
- ✅ **ปรับสัดส่วนชุด** — Stretch X/Y (ยืด/หดความกว้าง/สูง)
- ✅ **EMA Smoothing** — ลดการกระพริบของชุด
- ✅ **Multi-Page HUD** — กด `H` สลับหน้า Basic/Tuning
- ✅ **บันทึกภาพ** — กด `P` บันทึกภาพลงโฟลเดอร์ `captures/`
- ✅ **FPS Counter** — แสดงประสิทธิภาพแบบ real-time พร้อมสีเตือน
- ✅ **Camera Error Handling** — ลองใหม่ 30 ครั้งก่อนปิดโปรแกรม
- ✅ **Resize Cache** — ลดภาระ CPU
- ✅ **uint16 Blending** — เร็วกว่า float32 2-3 เท่า

---

## 📁 โครงสร้างโปรเจกต์
suit-try-on/
├─ assets/ # ไฟล์ทรัพยากร
│ ├─ female_suit_1.png # รูปชุดผู้หญิง 1
│ ├─ female_suit_2.png # รูปชุดผู้หญิง 2
│ ├─ male_suit_1.png # รูปชุดผู้ชาย 1
│ ├─ male_suit_2.png # รูปชุดผู้ชาย 2
│ └─ pose_landmarker_lite.task # โมเดล MediaPipe
│
├─ captures/ # 📸 โฟลเดอร์บันทึกภาพ (สร้างอัตโนมัติ)
│ └─ tryon_YYYYMMDD_HHMMSS.jpg # ภาพที่บันทึกเมื่อกด P
│
├─ config.py # Configuration (ค่า tuning ของชุด)
├─ main.py # Controller + HUD + Main Loop
├─ tryon_engine.py # Business Logic (Pose Detection + Rendering)
├─ requirements.txt # Dependencies
├─ test.py # Script ทดสอบ
│
├─ README.md # ไฟล์นี้ (ภาพรวมโปรเจกต์)
├─ setup_windows.md # 🪟 คู่มือติดตั้ง Windows
├─ setup_macos.md # 🍎 คู่มือติดตั้ง macOS
├─ USAGE.md # 🎮 คู่มือการใช้งานฉบับเต็ม
└─ TROUBLESHOOTING.md # 🔧 แก้ปัญหาที่พบบ่อย

### 📝 คำอธิบายโฟลเดอร์และไฟล์

| ไฟล์/โฟลเดอร์ | คำอธิบาย |
|--------------|----------|
| `assets/` | ไฟล์ทรัพยากร — รูปสูท PNG พื้นหลังโปร่งใส + โมเดล MediaPipe |
| `captures/` | 📸 **สร้างอัตโนมัติ** เมื่อกด `P` — เก็บภาพที่บันทึก |
| `config.py` | Configuration — ค่า tuning ของแต่ละชุด (offset, stretch, anchor) |
| `main.py` | Controller — Main loop, HUD, Keyboard handling |
| `tryon_engine.py` | Business Logic — Pose detection, Suit rendering, Smoothing |
| `requirements.txt` | Dependencies — ระบุเวอร์ชัน library ที่ใช้ |
| `setup_windows.md` | คู่มือติดตั้งสำหรับ Windows (สำหรับมือใหม่) |
| `setup_macos.md` | คู่มือติดตั้งสำหรับ macOS (สำหรับมือใหม่) |
| `USAGE.md` | คู่มือการใช้งานฉบับเต็ม — ปุ่มลัดทั้งหมด + Workflow |
| `TROUBLESHOOTING.md` | รวบรวมปัญหาที่พบบ่อยและวิธีแก้ |

---

## 🚀 เริ่มต้นใช้งาน

### เลือกคู่มือตามระบบปฏิบัติการของคุณ:

| ระบบปฏิบัติการ | คู่มือ |
|---------------|--------|
| 🪟 **Windows** | [📖 setup_windows.md](setup_windows.md) |
| 🍎 **macOS** | [📖 setup_macos.md](setup_macos.md) |

### 📖 คู่มืออื่นๆ

- 🎮 [USAGE.md](USAGE.md) — วิธีใช้งานและปุ่มลัดทั้งหมด
- 🔧 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — แก้ปัญหาที่พบบ่อย

---

## ⚡ Quick Start (สำหรับคนที่เคยทำแล้ว)

### 🪟 Windows

```cmd
cd C:\Projects\suit-try-on
.venv\Scripts\activate
python main.py

### Mac OS

cd ~/Projects/suit-try-on
source .venv/bin/activate
python main.py

### ปุ่มหลัก (หน้า Basic)

| ปุ่ม | คำสั่ง |
|-----|--------|
| `S` | เปลี่ยนสูท |
| `F` | สลับเพศ |
| `H` | สลับไปหน้า Tuning |
| `P` | 📸 บันทึกภาพ |
| `Q` | ปิดโปรแกรม |

### ปุ่มปรับแต่ง (หน้า Tuning — กด H เพื่อเข้า)

| ปุ่ม | คำสั่ง |
|-----|--------|
| `T` | เปิด/ปิด Smoothing |
| `+` / `-` | ปรับ Alpha |
| `[` / `]` | เลื่อน X ±1px |
| `{` / `}` | เลื่อน X ±5px |
| `I` / `K` | เลื่อน Y ±1px |
| `A` / `D` | Stretch X |
| `W` / `X` | Stretch Y |
| `R` | Reset Stretch |