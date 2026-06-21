# 🪟 ติดตั้งและรัน Virtual Suit Try-On บน Windows

คู่มือนี้ **เขียนสำหรับคนที่ไม่เคยเปิด Command Prompt มาก่อน** — ทำตามทีละขั้นตอนได้เลยครับ

---

## 🔰 ก่อนเริ่ม ขอให้เข้าใจภาพรวมก่อน

โปรแกรมนี้ต้องใช้ 4 สิ่งประกอบกัน:

```
Python 3.12     ← ภาษาที่ใช้รัน
     +
opencv-python   ← เปิดกล้อง + แสดงรูป
mediapipe       ← จับตำแหน่งร่างกาย
numpy           ← คำนวณตัวเลข
     +
assets/         ← รูปสูท + โมเดล
     +
main.py         ← ตัวโปรแกรม
```

---

## 📦 ขั้นตอนที่ 1: ติดตั้ง Python 3.12.x

### 1.1 เปิดเว็บเบราว์เซอร์ (Chrome / Edge)

ไปที่: https://www.python.org/downloads/

### 1.2 กดปุ่มสีเหลือง "Download Python 3.12.x"

(ตัวเลขอาจเป็น 3.12.5, 3.12.6, 3.12.7 — เลขมากสุดคือใหม่สุด)

### 1.3 เปิดไฟล์ที่โหลดมา ดับเบิลคลิก

### 1.4 ⚠️ สำคัญมาก: ที่หน้าจอแรก **ต้องติ๊กถูกที่ข้อความนี้**

```
☐ Install launcher for all users (recommended)
☑ **Add Python 3.12 to PATH**   ← ติ๊กอันนี้ด้วย!
```

### 1.5 กด "Install Now" → รอจนขึ้น "Setup was successful" → กด "Close"

### 1.6 ทดสอบว่า Python ทำงาน

- กดปุ่ม `Windows` ที่คีย์บอร์ด
- พิมพ์ `cmd` → Enter (จะเปิดหน้าต่างสีดำ ชื่อ Command Prompt)
- พิมพ์:

```cmd
python --version
```

- ถ้าขึ้น `Python 3.12.x` → ✅ สำเร็จ

---

## 📁 ขั้นตอนที่ 2: โหลดโปรเจกต์จาก GitHub

### 2.1 เปิด Command Prompt (หน้าต่างสีดำ)

กด `Windows` → พิมพ์ `cmd` → Enter

### 2.2 สร้างโฟลเดอร์ Projects (ถ้ายังไม่มี)

ค่อยๆ พิมพ์ทีละบรรทัด กด Enter หลังแต่ละบรรทัด:

```cmd
cd C:\
mkdir Projects
```

### 2.3 เข้าไปในโฟลเดอร์ Projects แล้วโหลดโปรเจกต์

```cmd
cd Projects
git clone -b refactor/error-handling-improvements https://github.com/jamorn/suit-try-on.git
```

> ⚠️ **ถ้าขึ้น `'git' is not recognized`** → ยังไม่มี Git ให้ลงจาก https://git-scm.com/download/win (กด Next อย่างเดียวจนจบ) แล้วเปิด `cmd` ใหม่ แล้วเริ่มขั้นตอน 2.3 ใหม่

### 2.4 เข้าไปในโฟลเดอร์โปรเจกต์

```cmd
cd suit-try-on
```

### 2.5 ตรวจสอบว่ามีไฟล์อะไรบ้าง

```cmd
dir
```

ต้องเห็นชื่อไฟล์ประมาณนี้:

```
config.py
main.py
tryon_engine.py
requirements.txt
assets (folder)
```

---

## 🔧 ขั้นตอนที่ 3: สร้าง Virtual Environment (.venv)

Virtual Environment คือ **"โฟลเดอร์พิเศษ"** ที่แยก Python + Library ของโปรเจกต์นี้ออกจากเครื่องเรา ป้องกันชนกับโปรแกรมอื่น

### 3.1 สร้าง .venv

**ยังอยู่ในหน้าต่าง Command Prompt เดิม** — ในโฟลเดอร์ `C:\Projects\suit-try-on`

พิมพ์:

```cmd
python -m venv .venv
```

รอสักครู่ จะกลับมาที่光标เฉยๆ (ไม่มี error)

### 3.2 เปิดใช้งาน .venv

พิมพ์:

```cmd
.venv\Scripts\activate
```

ถ้าสำเร็จ จะเห็น **`.venv`** โผล่มาด้านหน้าซ้าย:

```
(.venv) C:\Projects\suit-try-on>
```

### 3.3 เช็คว่า .venv ทำงานจริง

พิมพ์:

```cmd
where.exe python
```

ต้องขึ้น path ที่มี `.venv` อยู่:

```
C:\Projects\suit-try-on\.venv\Scripts\python.exe
```

> ⚠️ **มือใหม่พลิกตรงนี้บ่อยมาก!** ถ้าเห็น `C:\Users\...\Python312\python.exe` แสดงว่ายังไม่ได้ Activate .venv → พิมพ์ `.venv\Scripts\activate` อีกครั้ง

---

## 📥 ขั้นตอนที่ 4: ติดตั้ง Library

**ตรวจสอบอีกครั้งว่าเห็น `(.venv)` อยู่ด้านซ้ายมือ** แล้วค่อยพิมพ์:

```cmd
python -m pip install -r requirements.txt
```

รอประมาณ 1-3 นาที จะขึ้นข้อความประมาณนี้:

```
Successfully installed mediapipe-0.10.x numpy-1.26.x opencv-python-4.x.x
```

### ตรวจสอบว่าติดตั้งครบ

```cmd
python -m pip list
```

ต้องเห็น:

| ชื่อ Package    |
|-----------------|
| mediapipe       |
| opencv-python   |
| numpy           |

---

## 📂 ขั้นตอนที่ 5: เตรียมไฟล์ Model + รูปสูท

### 5.1 เช็คว่ามี folder assets หรือยัง

```cmd
dir
```

ถ้าไม่เห็น `assets` ให้พิมพ์:

```cmd
mkdir assets
```

### 5.2 เช็คของใน assets

```cmd
dir assets
```

ควรมีไฟล์เหล่านี้:

| ไฟล์                          | ได้จาก                                   |
|------------------------------|------------------------------------------|
| `pose_landmarker_lite.task`  | ดาวน์โหลดเอง (ขั้นตอน 5.3)               |
| `male_suit_1.png`            | หา PNG สูทผู้ชาย (ขั้นตอน 5.4)          |
| `male_suit_2.png`            | หา PNG สูทผู้ชาย                         |
| `female_suit_1.png`          | หา PNG สูทผู้หญิง                        |
| `female_suit_2.png`          | หา PNG สูทผู้หญิง                        |

### 5.3 ดาวน์โหลดโมเดล MediaPipe (จำเป็น!)

เปิดเว็บนี้ในเบราว์เซอร์:

https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task

กด `Ctrl + S` (Save) → เลือกโฟลเดอร์ `C:\Projects\suit-try-on\assets\` → บันทึก

### 5.4 หารูปสูท PNG

- เปิด Google → ค้นหา `suit png transparent` (หรือ `blazer png`, `suit png`)
- เลือกรูปที่มีพื้นหลังโปร่งใส (เห็นตาหมากรุก)
- คลิกขวา → Save image as → บันทึกใน `C:\Projects\suit-try-on\assets\`
- ตั้งชื่อตามนี้:
  - `male_suit_1.png`
  - `male_suit_2.png`
  - `female_suit_1.png`
  - `female_suit_2.png`

---

## 🎬 ขั้นตอนที่ 6: รันโปรแกรม!

**ให้อยู่ใน Command Prompt ที่มี `(.venv)` และอยู่ในโฟลเดอร์ `C:\Projects\suit-try-on`**

พิมพ์:

```cmd
.venv\Scripts\python.exe main.py
```

จะเห็นหน้าจอเปิดขึ้นมาแสดงภาพจากกล้อง พร้อมสูทที่ร่างกายคุณ!

---

## 🎮 ขั้นตอนที่ 7: วิธีใช้งาน

ขณะที่โปรแกรมรันอยู่ — กดปุ่มบนคีย์บอร์ด:

| ปุ่ม | คำสั่ง                       |
|-----|-----------------------------|
| `S` | เปลี่ยนสูท                  |
| `F` | สลับเพศ (ชาย → หญิง)       |
| `T` | เปิด/ปิด Smooth (ลดสั่น)    |
| `Q` | ปิดโปรแกรม                  |

---

## ❗ ขั้นตอนที่ 8: ปัญหาที่พบบ่อย

### 8.1 Error: python ไม่เจอ

```
'python' is not recognized
```

→ ลง Python ใหม่ อย่าลืมติ๊ก **"Add Python to PATH"**

### 8.2 Error: ไม่เจอกล้อง

```
ERROR:main:ไม่สามารถเปิดกล้องได้
```

→ ปิดโปรแกรมอื่นที่ใช้กล้อง (Zoom, Teams, OBS)

### 8.3 เปิดกล้องแล้วค้างสีดำ

→ ลองรันใหม่ หรือเสียบกล้องใหม่

### 8.4 Error ตอน git clone

```
'git' is not recognized
```

→ ลง Git จาก https://git-scm.com/download/win

### 8.5 Error ตอน import NormalizedLandmark

→ รัน:

```cmd
python -m pip install --upgrade mediapipe
```

---

## 🚀 รวบรัด สำหรับคนที่เคยทำแล้ว

```cmd
cd C:\Projects\suit-try-on
.venv\Scripts\activate
.venv\Scripts\python.exe main.py
```

---

สนุกกับการลองเสื้อผ้าจริง! 👔👗
