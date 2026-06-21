# 🪟 ติดตั้งและรัน Virtual Suit Try-On บน Windows

คู่มือนี้สำหรับ **มือใหม่ที่ใช้ Windows ครั้งแรก** ตั้งแต่ลง Python จนถึงรันโปรแกรมเห็นหน้าคนในกล้อง

---

## 📦 1. ติดตั้ง Python 3.12.x

### 1.1 ดาวน์โหลด

ไปที่ https://www.python.org/downloads/ → เลือก **Python 3.12.x** (เช่น 3.12.5)

> ⚠️ **สำคัญ:** ตอนติดตั้ง **ต้อง勾选 (ติ๊ก) "Add Python to PATH"** ที่หน้าจอแรก มิฉะนั้นจะเรียก `python` ไม่เจอ

### 1.2 ตรวจสอบหลังติดตั้ง

เปิด **Command Prompt** (หรือ Terminal, PowerShell) แล้วพิมพ์:

```cmd
python --version
```

ต้องขึ้นว่า `Python 3.12.x`

```cmd
where.exe python
```

ควรเห็น path คล้าย:
```
C:\Users\<ชื่อคุณ>\AppData\Local\Programs\Python\Python312\python.exe
```

---

## 📁 2. โคลนโปรเจกต์จาก GitHub

```cmd
cd C:\
mkdir Projects
cd Projects
git clone -b refactor/error-handling-improvements https://github.com/jamorn/suit-try-on.git
cd suit-try-on
```

> 💡 ถ้าไม่มี `git` ให้ลงจาก https://git-scm.com/download/win (เลือก Git for Windows, ค่าเริ่มต้นทั้งหมด Next ได้เลย)

หลังจาก clone เสร็จ ให้ตรวจสอบว่ามีไฟล์เหล่านี้:

```cmd
dir
```

ต้องเห็น:
```
config.py
main.py
tryon_engine.py
requirements.txt
assets/
```

---

## 🔧 3. สร้าง Virtual Environment (⚠️ จุดที่มือใหม่พลิกบ่อย)

### 3.1 สร้าง .venv

```cmd
python -m venv .venv
```

### 3.2 เปิดใช้งาน (Activate)

```cmd
.venv\Scripts\activate
```

ถ้าสำเร็จ จะเห็น `(.venv)` ขึ้นด้านหน้าซ้าย:

```
(.venv) C:\Projects\suit-try-on>
```

### 3.3 เช็คว่าอยู่ใน .venv จริงหรือไม่

```cmd
where.exe python
```

ต้องขึ้น path เป็น:
```
C:\Projects\suit-try-on\.venv\Scripts\python.exe
```

> ⚠️ **⚠️ ปัญหาที่พบบ่อย:** ถ้าเห็น `C:\Users\...\Python312\python.exe` แสดงว่ายังไม่ได้ activate .venv — `pip install` จะไปลงที่ Global Python แทน

**วิธีแก้:** รัน `.venv\Scripts\activate` อีกครั้ง แล้ว `where.exe python` เช็คให้แน่ใจ

---

## 📥 4. ติดตั้ง Library (opencv-python, mediapipe, numpy)

**เมื่อมั่นใจว่า `(.venv)` แสดงอยู่** ให้รัน:

```cmd
python -m pip install -r requirements.txt
```

หรือติดตั้งทีละตัว:

```cmd
python -m pip install mediapipe opencv-python "numpy>=1.24.0,<2.0.0"
```

รอจนขึ้น `Successfully installed ...` (ใช้เวลาประมาณ 1-3 นาที)

ตรวจสอบ:

```cmd
python -m pip list
```

ต้องเห็น:

| Package        | Version   |
|----------------|-----------|
| opencv-python  | >= 4.8    |
| mediapipe      | >= 0.10   |
| numpy          | 1.2x.x    |

---

## 📂 5. ตรวจสอบไฟล์ Model และรูปสูท

### 5.1 โมเดล MediaPipe

เข้าไปที่ `assets/` โฟลเดอร์:

```cmd
dir assets
```

ต้องมีไฟล์: `pose_landmarker_lite.task`

> 💡 ถ้าไม่มี ให้ดาวน์โหลดจาก:
> https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task
> แล้ววางไว้ใน `assets/`

### 5.2 รูปสูท (PNG พื้นโปร่งใส)

สร้างหรือวางไฟล์ PNG สูทในโฟลเดอร์ `assets/`:

- `male_suit_1.png`
- `male_suit_2.png`
- `female_suit_1.png`
- `female_suit_2.png`

> ตัวอย่างสูท PNG: https://www.freepngs.com/ (ค้นหา suit หรือ blazer)

---

## 🎬 6. รันโปรแกรม

### 6.1 รันตรง ๆ (แนะนำ)

```cmd
.venv\Scripts\python.exe main.py
```

### 6.2 รันผ่าน VS Code

1. เปิด VS Code:
   ```cmd
   code .
   ```
2. กด `Ctrl+Shift+P` → พิมพ์ `Python: Select Interpreter`
3. เลือก `./.venv/Scripts/python.exe`
4. เปิดไฟล์ `main.py` → กดปุ่ม ▶️ (Run) มุมขวาบน

---

## 🎮 7. การใช้งาน

| ปุ่ม | คำสั่ง                     |
|-----|---------------------------|
| `S` | เปลี่ยนสูท                |
| `F` | สลับเพศ (ชาย/หญิง)        |
| `T` | เปิด/ปิด Smoothing        |
| `Q` | ออกจากโปรแกรม             |

---

## ❗ 8. ปัญหาที่พบบ่อย (Troubleshooting)

### ไฟล์ไม่เข้า cache

```
WARNING:tryon_engine:ไม่พบไฟล์รูป assets/male_suit_1.png
```

**แก้:** ตรวจสอบว่าไฟล์ PNG อยู่ใน `assets/` จริง และชื่อตรงกับใน `config.py`

### ไม่เจอกล้อง

```
ERROR:main:ไม่สามารถเปิดกล้องได้
```

**แก้:** ตรวจสอบว่า Webcam ต่ออยู่ หรือไม่มีโปรแกรมอื่นใช้กล้องอยู่ (Zoom, Teams, OBS)

### MediaPipe import error

ถ้าขึ้น error เกี่ยวกับ `NormalizedLandmark`:

**แก้:** รัน `python -m pip install --upgrade mediapipe` หรือตรวจสอบ mediapipe version:

```cmd
python -m pip show mediapipe
```

ต้องเป็น `0.10.x`

---

## ✅ สรุปคำสั่งแบบรวบรัด (สำหรับคนที่เคยทำแล้ว)

```cmd
cd C:\Projects\suit-try-on
.venv\Scripts\activate
python -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

---

สนุกกับการลองเสื้อผ้าจริง! 👔👗
