import cv2
import os
import sys
from typing import Any
import numpy as np
import mediapipe as mp
from config import SUIT_DATA, MODEL_PATH, SuitConfig

# --- Constants ---
SHOULDER_SCALE = 1.5
SMOOTH_ALPHA_DEFAULT = 0.5
BOTTOM_BAR_HEIGHT = 80


class SuitTryOnApp:
    def __init__(self) -> None:
        # ตรวจสอบไฟล์โมเดล
        if not os.path.exists(MODEL_PATH):
            print(f"Error: ไม่พบไฟล์โมเดล {MODEL_PATH}")
            sys.exit(1)

        base_options = mp.tasks.BaseOptions(model_asset_path=MODEL_PATH)
        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.IMAGE
        )
        self.detector: Any = mp.tasks.vision.PoseLandmarker.create_from_options(
            options)
        self.all_suits_configs: list[SuitConfig] = SUIT_DATA
        self.active_suits_configs: list[SuitConfig] = []
        self.current_suit_idx: int = 0
        self.current_sex: str | None = None

        # Cache รูปสูท: โหลดเก็บไว้ใน Dict เพื่อไม่ให้อ่าน Disk ทุกเฟรม
        self.suit_cache: dict[str, np.ndarray] = {}
        for s in self.all_suits_configs:
            if not os.path.exists(s.path):
                print(f"Warning: ไม่พบไฟล์รูป {s.path}")
                continue
            img = cv2.imread(s.path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                self.suit_cache[s.path] = img

        if not self.suit_cache:
            print("Error: ไม่มีรูปสูทที่โหลดได้เลย")
            sys.exit(1)

        # EMA Smoothing (Optional)
        self.smoothing_enabled: bool = False
        self.smooth_alpha: float = SMOOTH_ALPHA_DEFAULT
        self._smooth_center_x: int | None = None
        self._smooth_center_y: int | None = None

    def set_user_sex(self, sex: str) -> None:
        self.current_sex = sex
        filtered = [s for s in self.all_suits_configs if s.sex
                    == sex and s.enabled]
        if not filtered:
            print(f"Warning: ไม่มีสูทสำหรับเพศ '{sex}' คงค่าเดิม")
            return
        self.active_suits_configs = sorted(filtered, key=lambda x: x.order)
        self.current_suit_idx = 0

    def overlay_suit(
        self,
        frame: np.ndarray,
        landmarks_list: Any,
    ) -> np.ndarray:
        if not self.active_suits_configs:
            return frame

        config = self.active_suits_configs[self.current_suit_idx]
        # ใช้ Cache แทนการอ่านไฟล์ทุกเฟรม
        suit_img = self.suit_cache.get(config.path)
        if suit_img is None:
            return frame

        h, w, _ = frame.shape

        # เลือกคนที่มีไหล่กว้างที่สุด (ใกล้กล้องมากที่สุด)
        if len(landmarks_list) > 1:
            best_idx = 0
            best_width = 0
            for i, lm in enumerate(landmarks_list):
                lx = lm[11].x
                rx = lm[12].x
                shld_w = abs(lx - rx)
                if shld_w > best_width:
                    best_width = shld_w
                    best_idx = i
            landmarks = landmarks_list[best_idx]
        else:
            landmarks = landmarks_list[0]
        l_shld = landmarks[11]
        r_shld = landmarks[12]

        # 1. คำนวณขนาดตามความกว้างไหล่
        shld_width = int(abs(l_shld.x - r_shld.x) * w * SHOULDER_SCALE)
        aspect_ratio = suit_img.shape[0] / suit_img.shape[1]
        suit_h = int(shld_width * aspect_ratio)

        # 2. Resize ภาพสูท
        suit_resized = cv2.resize(suit_img, (shld_width, suit_h))

        # 3. คำนวณตำแหน่งกึ่งกลาง
        center_y = int((l_shld.y + r_shld.y) / 2 * h) - \
            int(shld_width * config.y_offset)
        center_x = int((l_shld.x + r_shld.x) / 2 * w)

        # 4. EMA Smoothing (ถ้าเปิดใช้งาน)
        if self.smoothing_enabled:
            if self._smooth_center_x is None:
                self._smooth_center_x = center_x
                self._smooth_center_y = center_y
            else:
                self._smooth_center_x = int(
                    self.smooth_alpha * center_x + (1 - self.smooth_alpha) * self._smooth_center_x)
                self._smooth_center_y = int(
                    self.smooth_alpha * center_y + (1 - self.smooth_alpha) * self._smooth_center_y)
            center_x, center_y = self._smooth_center_x, self._smooth_center_y

        # 5. คำนวณขอบเขต (ซ้ายบน-ขวาล่าง)
        y1 = center_y - suit_h // 2
        y2 = center_y + suit_h // 2
        x1 = center_x - shld_width // 2
        x2 = center_x + shld_width // 2

        # 6. Clipping: ตัดส่วนที่เกินขอบเฟรมทิ้ง
        # หาขอบเขตที่มองเห็นได้บน frame
        frame_y1 = max(0, y1)
        frame_y2 = min(h, y2)
        frame_x1 = max(0, x1)
        frame_x2 = min(w, x2)

        # หาขอบเขตที่ตรงกันบนภาพสูท
        crop_y1 = frame_y1 - y1
        crop_y2 = crop_y1 + (frame_y2 - frame_y1)
        crop_x1 = frame_x1 - x1
        crop_x2 = crop_x1 + (frame_x2 - frame_x1)

        # ถ้าส่วนที่แสดงผลมีขนาดพอดี
        if frame_y2 > frame_y1 and frame_x2 > frame_x1 and crop_y2 > crop_y1 and crop_x2 > crop_x1:
            roi = frame[frame_y1:frame_y2, frame_x1:frame_x2]
            suit_cropped = suit_resized[crop_y1:crop_y2, crop_x1:crop_x2]

            # 7. Alpha Blending — ใช้ Alpha Channel ให้ขอบเนียน
            if suit_cropped.shape[2] == 4:
                alpha = suit_cropped[:, :, 3:4] / 255.0
                suit_rgb = suit_cropped[:, :, :3].astype(np.float32)
                roi_f = roi.astype(np.float32)
                blended = (1 - alpha) * roi_f + alpha * suit_rgb
                roi[:, :, :] = blended.astype(np.uint8)
            else:
                # Fallback: ถ้าไม่มี Alpha Channel ให้วางทับแบบทึบ
                frame[y1:y2, x1:x2] = suit_cropped[:, :, :3]

        return frame

    def toggle_smoothing(self) -> None:
        self.smoothing_enabled = not self.smoothing_enabled
        # Reset ค่า Smooth เมื่อปิด-เปิด เพื่อไม่ให้残留ค่าเก่า
        self._smooth_center_x = None
        self._smooth_center_y = None
        status = "ON" if self.smoothing_enabled else "OFF"
        print(f"EMA Smoothing: {status} (alpha={self.smooth_alpha})")

    def switch_suit(self) -> None:
        if self.active_suits_configs:
            self.current_suit_idx = (
                self.current_suit_idx + 1) % len(self.active_suits_configs)
