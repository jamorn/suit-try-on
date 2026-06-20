# tryon_engine.py
import logging
import cv2
import os
from collections.abc import Sequence
from dataclasses import dataclass
import numpy as np
import mediapipe as mp
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmark
from config import SUIT_DATA, MODEL_PATH, SuitConfig

logger = logging.getLogger(__name__)

# --- Constants ---
SHOULDER_SCALE = 1.5
SMOOTH_ALPHA_DEFAULT = 0.5
LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12

# --- Types ---
PoseLandmarkList = Sequence[NormalizedLandmark]
LandmarkListSequence = Sequence[PoseLandmarkList]


@dataclass(slots=True)
class SuitRect:
    """ตำแหน่งและขนาดของสูทบน frame"""
    x: int
    y: int
    width: int
    height: int


class SuitRenderer:
    """จัดการเรื่องการคำนวณตำแหน่งและวางภาพสูทลงบน frame"""

    def __init__(self, suit_cache: dict[str, np.ndarray]) -> None:
        self.suit_cache = suit_cache
        self.smoothing_enabled: bool = False
        self.smooth_alpha: float = SMOOTH_ALPHA_DEFAULT
        self._smooth_center_x: float | None = None
        self._smooth_center_y: float | None = None

    def render(
        self,
        frame: np.ndarray,
        landmarks_list: LandmarkListSequence,
        config: SuitConfig,
    ) -> np.ndarray:
        """วางสูทลงบน frame"""
        if not landmarks_list:
            return frame

        suit_img = self.suit_cache.get(config.path)
        if suit_img is None:
            return frame

        landmarks = self._select_person(landmarks_list)
        if landmarks is None:
            return frame

        rect = self._calculate_suit_rect(frame.shape, landmarks, suit_img, config.y_offset)
        self._blend(frame, suit_img, rect)

        return frame

    def toggle_smoothing(self) -> None:
        self.smoothing_enabled = not self.smoothing_enabled
        self._smooth_center_x = None
        self._smooth_center_y = None
        status = "ON" if self.smoothing_enabled else "OFF"
        logger.info("EMA Smoothing: %s (alpha=%s)", status, self.smooth_alpha)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _select_person(landmarks_list: LandmarkListSequence) -> PoseLandmarkList | None:
        """เลือกคนที่อยู่ใกล้กล้องที่สุด (ไหล่กว้างที่สุด)"""
        valid = [lm for lm in landmarks_list if len(lm) > RIGHT_SHOULDER]
        if not valid:
            return None
        return max(
            valid,
            key=lambda lm: abs(lm[LEFT_SHOULDER].x - lm[RIGHT_SHOULDER].x),
        )

    def _calculate_suit_rect(
        self,
        frame_shape: tuple[int, ...],
        landmarks: PoseLandmarkList,
        suit_img: np.ndarray,
        y_offset: float,
    ) -> SuitRect:
        """คำนวณตำแหน่งและขนาดของสูทที่ต้องการวาง"""
        h, w = frame_shape[:2]

        left_shld = landmarks[LEFT_SHOULDER]
        right_shld = landmarks[RIGHT_SHOULDER]

        shoulder_width = max(1, int(abs(left_shld.x - right_shld.x) * w * SHOULDER_SCALE))
        aspect = suit_img.shape[0] / suit_img.shape[1]
        suit_height = int(shoulder_width * aspect)

        center_x = int((left_shld.x + right_shld.x) * w / 2)
        center_y = int((left_shld.y + right_shld.y) * h / 2) - int(shoulder_width * y_offset)

        if self.smoothing_enabled:
            center_x, center_y = self._smooth(center_x, center_y)

        return SuitRect(x=center_x, y=center_y, width=shoulder_width, height=suit_height)

    def _smooth(self, x: int, y: int) -> tuple[int, int]:
        """EMA Smoothing ลดการกระตุก (เก็บค่า float ป้องกัน Sticky Effect)"""
        if self._smooth_center_x is None:
            self._smooth_center_x = float(x)
            self._smooth_center_y = float(y)
        else:
            alpha = self.smooth_alpha
            self._smooth_center_x = alpha * x + (1 - alpha) * self._smooth_center_x
            self._smooth_center_y = alpha * y + (1 - alpha) * self._smooth_center_y
        return int(self._smooth_center_x), int(self._smooth_center_y)

    @staticmethod
    def _blend(
        frame: np.ndarray,
        suit_img: np.ndarray,
        rect: SuitRect,
    ) -> None:
        """วางภาพสูทลงบน frame พร้อม Clipping และ Alpha Blending"""
        if rect.width <= 0 or rect.height <= 0:
            return

        h, w = frame.shape[:2]

        cx, cy = rect.x, rect.y
        sw, sh = rect.width, rect.height

        suit_resized = cv2.resize(suit_img, (sw, sh))

        y1 = cy - sh // 2
        y2 = y1 + sh
        x1 = cx - sw // 2
        x2 = x1 + sw

        # Clipping
        frame_y1 = max(0, y1)
        frame_y2 = min(h, y2)
        frame_x1 = max(0, x1)
        frame_x2 = min(w, x2)

        roi_h = frame_y2 - frame_y1
        roi_w = frame_x2 - frame_x1

        if roi_h <= 0 or roi_w <= 0:
            return

        crop_y1 = frame_y1 - y1
        crop_y2 = crop_y1 + roi_h
        crop_x1 = frame_x1 - x1
        crop_x2 = crop_x1 + roi_w

        roi = frame[frame_y1:frame_y2, frame_x1:frame_x2]
        suit_cropped = suit_resized[crop_y1:crop_y2, crop_x1:crop_x2]

        # Alpha Blending
        if suit_cropped.ndim == 3 and suit_cropped.shape[2] == 4:
            # NOTE: `suit_cropped[:, :, 3:4] / 255.0` produces float64.
            # For ~5% speed gain, add `.astype(np.float32)` if FPS drops later.
            alpha = suit_cropped[:, :, 3:4] / 255.0
            suit_rgb = suit_cropped[:, :, :3].astype(np.float32)
            roi_f = roi.astype(np.float32)
            blended = (1 - alpha) * roi_f + alpha * suit_rgb
            roi[:, :, :] = blended.astype(np.uint8)
        else:
            # Fallback: วางทับแบบทึบ (ใช้ clipped coordinates)
            frame[frame_y1:frame_y2, frame_x1:frame_x2] = suit_cropped[:, :, :3]


class SuitTryOnApp:
    """จัดการ state การทำงานหลัก: กล้อง, การตรวจจับ pose, การเปลี่ยนสูท"""

    def __init__(self) -> None:
        # ตรวจสอบไฟล์โมเดล
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"ไม่พบไฟล์โมเดล {MODEL_PATH}")

        base_options = mp.tasks.BaseOptions(model_asset_path=MODEL_PATH)
        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.IMAGE
        )
        self.detector: mp.tasks.vision.PoseLandmarker = (
            mp.tasks.vision.PoseLandmarker.create_from_options(options)
        )

        # Suit config
        self.all_suits_configs: list[SuitConfig] = SUIT_DATA
        self.active_suits_configs: list[SuitConfig] = []
        self.current_suit_idx: int = 0
        self.current_sex: str | None = None

        # Cache รูปสูท
        suit_cache: dict[str, np.ndarray] = {}
        for s in self.all_suits_configs:
            if not os.path.exists(s.path):
                logger.warning("ไม่พบไฟล์รูป %s", s.path)
                continue
            img = cv2.imread(s.path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                suit_cache[s.path] = img

        if not suit_cache:
            raise RuntimeError("ไม่มีรูปสูทที่โหลดได้เลย")

        # Renderer
        self.renderer = SuitRenderer(suit_cache)

    def set_user_sex(self, sex: str) -> None:
        """Filter suit list by sex and reset current index."""
        filtered = [s for s in self.all_suits_configs if s.sex == sex and s.enabled]
        if not filtered:
            logger.warning("ไม่มีสูทสำหรับเพศ '%s' คงค่าเดิม (%s)", sex, self.current_sex)
            return
        self.current_sex = sex
        self.active_suits_configs = sorted(filtered, key=lambda x: x.order)
        self.current_suit_idx = 0

    @property
    def smoothing_enabled(self) -> bool:
        return self.renderer.smoothing_enabled

    def overlay_suit(
        self,
        frame: np.ndarray,
        landmarks_list: LandmarkListSequence,
    ) -> np.ndarray:
        if not self.active_suits_configs:
            return frame

        config = self.active_suits_configs[self.current_suit_idx]
        return self.renderer.render(frame, landmarks_list, config)

    def toggle_smoothing(self) -> None:
        self.renderer.toggle_smoothing()

    def close(self) -> None:
        """ปิด MediaPipe Detector (คืน Resource C++)"""
        # detector is always created in __init__ unless constructor fails.
        if hasattr(self, "detector"):
            self.detector.close()

    def switch_suit(self) -> None:
        if not self.active_suits_configs:
            return
        self.current_suit_idx = (
            self.current_suit_idx + 1) % len(self.active_suits_configs)
