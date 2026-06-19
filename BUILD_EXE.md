# Building .exe สำหรับ SuitTryOn

## 1. ติดตั้ง PyInstaller

```powershell
pip install pyinstaller
```

---

## 2. วิธีที่ 1: Build เป็นโฟลเดอร์ (แนะนำ)

**ข้อดี:** ไฟล์ .exe เล็ก (~8 MB), เปิดโปรแกรมเร็ว  
**ข้อเสีย:** ต้องแจกทั้งโฟลเดอร์ (รวม ~200 MB)

```powershell
pyinstaller --onedir --windowed --add-data "assets;assets" main.py --name SuitTryOn
```

**ผลลัพธ์:**

```
dist/
└── SuitTryOn/
    ├── SuitTryOn.exe          # ตัวโปรแกรม (~8 MB)
    ├── *.dll, *.pyd           # ไฟล์ dependencies
    └── assets/                # รูปสูท + โมเดล
```

**การแจก:** ZIP ทั้งโฟลเดอร์ `SuitTryOn/` แล้วส่งไป

---

## 3. วิธีที่ 2: Build เป็นไฟล์ .exe เดียว

**ข้อดี:** แจกสะดวก (ไฟล์เดียว)  
**ข้อเสีย:** ไฟล์ใหญ่ (~250-300 MB), เปิดโปรแกรมช้าตอนแรก (ต้องแตกไฟล์ก่อน)

```powershell
pyinstaller --onefile --windowed --add-data "assets;assets" main.py --name SuitTryOn
```

**ผลลัพธ์:**

```
dist/
└── SuitTryOn.exe              # ไฟล์เดียว รวมทุกอย่าง (~250-300 MB)
```

---

## 4. Clean build (ถ้าต้องการ build ใหม่)

ลบของเก่าก่อน:

```powershell
Remove-Item -Recurse -Force dist, build, *.spec -ErrorAction SilentlyContinue
```

แล้วค่อยรัน build command ข้างบนอีกครั้ง

---

## 5. หมายเหตุ

- รองรับเฉพาะ **Windows** เท่านั้น
- ผู้ใช้ต้องมี **Webcam** เพื่อใช้งาน
- ถ้าไม่มีกล้อง โปรแกรมจะแสดง Error และปิด
- กด `q` เพื่อออกจากโปรแกรม
- กด `s` เพื่อสลับสูท
- กด `f` เพื่อเปลี่ยนเพศ (ชาย/หญิง)
- กด `t` เพื่อเปิด/ปิด Smoothing
