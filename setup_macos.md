# 🍎 ติดตั้งและรัน Virtual Suit Try-On บน macOS

คู่มือนี้เขียนสำหรับ **ผู้ใช้ Mac มือใหม่** — ทำตามทีละขั้นตอนได้เลยครับ

> 💡 **หมายเหตุ:** คู่มือนี้รองรับทั้ง **Intel Mac** และ **Apple Silicon (M1/M2/M3)**

---

## 🔰 ก่อนเริ่ม: ตรวจสอบ Mac ของคุณ

### คลิกเมนู Apple () มุมบนซ้าย → About This Mac

จะเห็นข้อมูลประมาณนี้:

```
Chip: Apple M1 (หรือ Intel Core i5)
Memory: 8 GB
macOS: Sonoma 14.x
```

**สำคัญ:**
- ถ้าเห็น **"Chip: Apple M1/M2/M3"** → คุณใช้ **Apple Silicon** (มีผลต่อการติดตั้ง)
- ถ้าเห็น **"Processor: Intel"** → คุณใช้ **Intel Mac**

---

## 📦 ขั้นตอนที่ 1: ติดตั้ง Homebrew (ตัวจัดการ Package)

Homebrew คือ "App Store สำหรับนักพัฒนา" — ใช้ติดตั้ง Python, Git และเครื่องมืออื่นๆ

### 1.1 เปิด Terminal

- กด `Command + Space` → พิมพ์ `Terminal` → Enter
- หรือเปิดจาก `Applications → Utilities → Terminal`

### 1.2 ติดตั้ง Homebrew

คัดลอกคำสั่งนี้ไปวางใน Terminal แล้วกด Enter:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

กด Enter เมื่อถูกถาม แล้วใส่รหัสผ่าน Mac ของคุณ (ตอนพิมพ์จะไม่เห็นตัวอักษร — เป็นเรื่องปกติ)

### 1.3 ⚠️ สำคัญมาก: เพิ่ม Homebrew เข้า PATH (สำหรับ Apple Silicon เท่านั้น)

หลังติดตั้งเสร็จ Terminal จะแสดงคำสั่งประมาณนี้:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**คัดลอก 2 บรรทัดนี้ไปวางใน Terminal แล้วกด Enter** (ถ้าไม่ทำ จะใช้ brew ไม่ได้)

### 1.4 ทดสอบว่า Homebrew ทำงาน

```bash
brew --version
```

ถ้าขึ้น `Homebrew 4.x.x` → ✅ สำเร็จ

---

## 🐍 ขั้นตอนที่ 2: ติดตั้ง Python 3.11

### ⚠️ ทำไมต้อง 3.11 ไม่ใช่ 3.12?

**MediaPipe** (library ที่ใช้จับร่างกาย) **ยังไม่รองรับ Python 3.12 บน macOS** อย่างสมบูรณ์ โดยเฉพาะ Apple Silicon

> 💡 ถ้าใช้ Python 3.12 จะเจอ error: `RuntimeError: Failed to generate graph`

### 2.1 ติดตั้ง Python 3.11 ผ่าน Homebrew

```bash
brew install python@3.11
```

รอสักครู่ (1-3 นาที)

### 2.2 ตรวจสอบว่าติดตั้งสำเร็จ

```bash
python3.11 --version
```

ต้องขึ้น `Python 3.11.x` → ✅ สำเร็จ

---

## 📁 ขั้นตอนที่ 3: โหลดโปรเจกต์จาก GitHub

### 3.1 ติดตั้ง Git (ถ้ายังไม่มี)

```bash
xcode-select --install
```

จะมีหน้าต่างเด้งขึ้นมา → กด "Install" → รอจนเสร็จ

### 3.2 สร้างโฟลเดอร์ Projects

```bash
mkdir -p ~/Projects
cd ~/Projects
```

### 3.3 โหลดโปรเจกต์

```bash
git clone https://github.com/jamorn/suit-try-on.git
cd suit-try-on
```

---

## 🔧 ขั้นตอนที่ 4: สร้าง Virtual Environment

### 4.1 สร้าง .venv ด้วย Python 3.11

```bash
python3.11 -m venv .venv
```

### 4.2 เปิดใช้งาน .venv

```bash
source .venv/bin/activate
```

ถ้าสำเร็จ จะเห็น **`(.venv)`** โผล่มาด้านหน้าซ้าย:

```
(.venv) yourname@MacBook suit-try-on %
```

### 4.3 ตรวจสอบว่า Python ใน .venv ถูกต้อง

```bash
python --version
```

ต้องขึ้น `Python 3.11.x` ✅

---

## 📥 ขั้นตอนที่ 5: ติดตั้ง Library

```bash
pip install -r requirements.txt
```

รอ 1-3 นาที จะขึ้น `Successfully installed ...`

### ⚠️ ถ้าเจอ error เกี่ยวกับ mediapipe

ลองอัปเดต pip ก่อน:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📂 ขั้นตอนที่ 6: เตรียมไฟล์ assets

### 6.1 สร้างโฟลเดอร์ assets

```bash
mkdir -p assets
```

### 6.2 ดาวน์โหลดโมเดล MediaPipe

เปิด Safari/Chrome → ไปที่:
https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task

ดาวน์โหลดแล้วลากไฟล์ไปวางใน `assets/`

### 6.3 หารูปสูท PNG

- ค้นหาจาก Google: `suit png transparent`
- เลือกรูปพื้นหลังโปร่งใส
- บันทึกใน `assets/` ตั้งชื่อ:
  - `male_suit_1.png`
  - `male_suit_2.png`
  - `female_suit_1.png`
  - `female_suit_2.png`

---

## 🎬 ขั้นตอนที่ 7: รันโปรแกรม

### 7.1 ตรวจสอบว่าอยู่ใน .venv และโฟลเดอร์ถูกต้อง

```bash
pwd
# ต้องขึ้น: /Users/yourname/Projects/suit-try-on

python --version
# ต้องขึ้น: Python 3.11.x
```

### 7.2 รันโปรแกรม

```bash
python main.py
```

### 7.3 ⚠️ สำคัญมาก: อนุญาตให้เข้าถึงกล้อง

**ครั้งแรกที่รัน** macOS จะถาม:

> **"Terminal" would like to access the camera.**

→ กด **"OK"** หรือ **"Allow"**

ถ้าไม่อนุญาต → กล้องจะเปิดไม่ได้ (ภาพดำ)

---

## 🎮 ขั้นตอนที่ 8: วิธีใช้งาน

ดูรายละเอียดเพิ่มเติมใน `USAGE.md`

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

---

## ❗ ปัญหาที่พบบ่อยบน macOS

### ❌ Error: "python3.11: command not found"

→ ยังไม่ได้ติดตั้ง Python 3.11 หรือยังไม่ได้เพิ่ม Homebrew เข้า PATH

**แก้:**
```bash
brew install python@3.11
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

---

### ❌ Error: "Failed to generate graph" (MediaPipe)

→ ใช้ Python 3.12 ซึ่งไม่รองรับ

**แก้:** ใช้ Python 3.11 แทน (ดูขั้นตอนที่ 2)

---

### ❌ กล้องเปิดไม่ได้ (ภาพดำ)

→ macOS ยังไม่อนุญาตให้ Terminal เข้าถึงกล้อง

**แก้:**
1. เปิด **System Settings** ( → System Settings)
2. ไปที่ **Privacy & Security → Camera**
3. หา **Terminal** → เปิดสวิตช์ให้เป็นสีเขียว
4. ปิด Terminal แล้วเปิดใหม่
5. รัน `python main.py` อีกครั้ง

---

### ❌ Error: "externally-managed-environment"

→ พยายามติดตั้ง library ลง Python ของระบบ (ไม่ใช่ .venv)

**แก้:** เปิดใช้งาน .venv ก่อน
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

### ❌ Error: "No module named 'mediapipe'"

→ ยังไม่ได้ activate .venv

**แก้:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

### ❌ รันแล้วช้ามาก / FPS ต่ำ

→ Mac กำลังใช้ GPU ไม่เต็มที่

**แก้:**
- ปิดแอปอื่นๆ ที่กินทรัพยากร (Chrome, Photoshop)
- ลดขนาดหน้าต่างโปรแกรม
- ใช้ `pose_landmarker_lite.task` (ไม่ใช่ full/heavy)

---

## 🔄 การรันครั้งถัดไป

หลังจากติดตั้งครั้งแรกแล้ว ครั้งต่อไปแค่:

```bash
cd ~/Projects/suit-try-on
source .venv/bin/activate
python main.py
```

---

## 🚀 รวบรัด (สำหรับคนเคยทำแล้ว)

```bash
cd ~/Projects/suit-try-on
source .venv/bin/activate
python main.py
```

---

## 📚 อ่านเพิ่มเติม

- 📖 `USAGE.md` — คู่มือการใช้งานฉบับเต็ม
- 🔧 `TROUBLESHOOTING.md` — แก้ปัญหาทั่วไป
- 🪟 `setup_windows.md` — สำหรับผู้ใช้ Windows

---

สนุกกับการลองเสื้อผ้าบน Mac! 🍎👔👗