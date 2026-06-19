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
        suit_img = self.suit_cache.get(config.path)
        if suit_img is None:
            return frame

        landmarks = self._select_person(landmarks_list)
        rect = self._calculate_suit_rect(frame.shape, landmarks, suit_img, config.y_offset)
        self._blend(frame, suit_img, rect)

        return frame

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    @staticmethod
    def _select_person(landmarks_list: Any) -> Any:
        """เลือกคนที่อยู่ใกล้กล้องที่สุด (ไหล่กว้างที่สุด)"""
        if len(landmarks_list) == 1:
            return landmarks_list[0]
        return max(
            landmarks_list,
            key=lambda lm: abs(lm[11].x - lm[12].x),
        )

    def _calculate_suit_rect(
        self,
        frame_shape: tuple[int, ...],
        landmarks: Any,
        suit_img: np.ndarray,
        y_offset: float,
    ) -> dict[str, int]:
        """คำนวณตำแหน่งและขนาดของสูทที่ต้องการวาง"""
        h, w = frame_shape[:2]

        left_shld = landmarks[11]
        right_shld = landmarks[12]

        shoulder_width = int(abs(left_shld.x - right_shld.x) * w * SHOULDER_SCALE)
        aspect = suit_img.shape[0] / suit_img.shape[1]
        suit_height = int(shoulder_width * aspect)

        center_x = int((left_shld.x + right_shld.x) * w / 2)
        center_y = int((left_shld.y + right_shld.y) * h / 2) - int(shoulder_width * y_offset)

        if self.smoothing_enabled:
            center_x, center_y = self._smooth(center_x, center_y)

        return {
            "x": center_x,
            "y": center_y,
            "width": shoulder_width,
            "height": suit_height,
        }

    def _smooth(
        self,
        x: int,
        y: int,
    ) -> tuple[int, int]:
        """EMA Smoothing ลดการกระตุก"""
        if self._smooth_center_x is None:
            self._smooth_center_x = x
            self._smooth_center_y = y
        else:
            alpha = self.smooth_alpha
            self._smooth_center_x = int(alpha * x + (1 - alpha) * self._smooth_center_x)
            self._smooth_center_y = int(alpha * y + (1 - alpha) * self._smooth_center_y)
        return self._smooth_center_x, self._smooth_center_y

    def _blend(
        self,
        frame: np.ndarray,
        suit_img: np.ndarray,
        rect: dict[str, int],
    ) -> None:
        """วางภาพสูทลงบน frame พร้อม Clipping และ Alpha Blending"""
        h, w = frame.shape[:2]

        cx, cy = rect["x"], rect["y"]
        sw, sh = rect["width"], rect["height"]

        # Resize สูท
        suit_resized = cv2.resize(suit_img, (sw, sh))

        # ขอบเขตของสูทบน frame
        y1 = cy - sh // 2
        y2 = cy + sh // 2
        x1 = cx - sw // 2
        x2 = cx + sw // 2

        # Clipping: ตัดส่วนที่เกินขอบเฟรม
        frame_y1 = max(0, y1)
        frame_y2 = min(h, y2)
        frame_x1 = max(0, x1)
        frame_x2 = min(w, x2)

        crop_y1 = frame_y1 - y1
        crop_y2 = crop_y1 + (frame_y2 - frame_y1)
        crop_x1 = frame_x1 - x1
        crop_x2 = crop_x1 + (frame_x2 - frame_x1)

        if not (frame_y2 > frame_y1 and frame_x2 > frame_x1 and
                crop_y2 > crop_y1 and crop_x2 > crop_x1):
            return

        roi = frame[frame_y1:frame_y2, frame_x1:frame_x2]
        suit_cropped = suit_resized[crop_y1:crop_y2, crop_x1:crop_x2]

        # Alpha Blending
        if suit_cropped.shape[2] == 4:
            alpha = suit_cropped[:, :, 3:4] / 255.0
            suit_rgb = suit_cropped[:, :, :3].astype(np.float32)
            roi_f = roi.astype(np.float32)
            blended = (1 - alpha) * roi_f + alpha * suit_rgb
            roi[:, :, :] = blended.astype(np.uint8)
        else:
            # Fallback: วางทับแบบทึบ
            frame[y1:y2, x1:x2] = suit_cropped[:, :, :3]

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
