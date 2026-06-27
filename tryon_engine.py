# tryon_engine.py
import logging
import time
import cv2
import os
from collections.abc import Sequence
from dataclasses import dataclass
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark
from config import SUIT_DATA, MODEL_PATH, SuitConfig

logger = logging.getLogger(__name__)  # ✅ แก้: name -> __name__

SMOOTH_ALPHA_DEFAULT = 0.5
LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12

PoseLandmarkList = Sequence[NormalizedLandmark]
LandmarkListSequence = Sequence[PoseLandmarkList]


@dataclass(slots=True)
class SuitRect:
    x: int
    y: int
    width: int
    height: int


class SuitRenderer:
    def __init__(self, suit_cache: dict[str, np.ndarray]) -> None:  # ✅ แก้: init -> __init__
        self.suit_cache = suit_cache
        self.smoothing_enabled: bool = False
        self.smooth_alpha: float = SMOOTH_ALPHA_DEFAULT
        self._smooth_center_x: float | None = None
        self._smooth_center_y: float | None = None

        # --- Resize Cache ---
        self._last_suit_path: str | None = None
        self._last_width: int = 0
        self._last_height: int = 0
        self._last_resized_suit: np.ndarray | None = None

    def render(
        self,
        frame: np.ndarray,
        landmarks_list: LandmarkListSequence,
        config: SuitConfig,
    ) -> np.ndarray:
        if not landmarks_list:
            return frame

        suit_img = self.suit_cache.get(config.path)
        if suit_img is None:
            return frame

        landmarks = self._select_person(landmarks_list)
        if landmarks is None:
            return frame

        rect = self._calculate_suit_rect(frame.shape, landmarks, suit_img, config)
        if rect.width <= 0 or rect.height <= 0:
            return frame

        # --- Resize Cache ---
        if (self._last_suit_path == config.path and
                self._last_width == rect.width and
                self._last_height == rect.height and
                self._last_resized_suit is not None):
            suit_resized = self._last_resized_suit
        else:
            suit_resized = cv2.resize(suit_img, (rect.width, rect.height))
            self._last_suit_path = config.path
            self._last_width = rect.width
            self._last_height = rect.height
            self._last_resized_suit = suit_resized

        self._blend(frame, suit_resized, rect)
        return frame

    def toggle_smoothing(self) -> None:
        self.smoothing_enabled = not self.smoothing_enabled
        self._smooth_center_x = None
        self._smooth_center_y = None
        status = "ON" if self.smoothing_enabled else "OFF"
        logger.info("EMA Smoothing: %s (alpha=%.2f)", status, self.smooth_alpha)

    def adjust_smoothing(self, delta: float) -> None:
        self.smooth_alpha = max(0.1, min(0.9, self.smooth_alpha + delta))
        self._smooth_center_x = None
        self._smooth_center_y = None
        logger.info("Smooth alpha ปรับเป็น: %.2f", self.smooth_alpha)

    @staticmethod
    def _select_person(landmarks_list: LandmarkListSequence) -> PoseLandmarkList | None:
        valid = [lm for lm in landmarks_list if len(lm) > RIGHT_SHOULDER]
        if not valid:
            return None
        return max(valid, key=lambda lm: abs(lm[LEFT_SHOULDER].x - lm[RIGHT_SHOULDER].x))

    def _calculate_suit_rect(
        self,
        frame_shape: tuple[int, ...],
        landmarks: PoseLandmarkList,
        suit_img: np.ndarray,
        config: SuitConfig,
    ) -> SuitRect:
        h, w = frame_shape[:2]

        left_shld = landmarks[LEFT_SHOULDER]
        right_shld = landmarks[RIGHT_SHOULDER]

        base_width = max(1, int(abs(left_shld.x - right_shld.x) * w * config.scale_factor))
        aspect = suit_img.shape[0] / suit_img.shape[1]
        suit_height = int(base_width * aspect)

        shld_center_x = int((left_shld.x + right_shld.x) * w / 2)
        shld_center_y = int((left_shld.y + right_shld.y) * h / 2)

        if self.smoothing_enabled:
            shld_center_x, shld_center_y = self._smooth(shld_center_x, shld_center_y)

        center_x = shld_center_x
        top_edge = shld_center_y - int(suit_height * config.anchor_y)
        max_bottom = h - 10

        if top_edge >= max_bottom:
            return SuitRect(x=0, y=0, width=0, height=0)

        suit_width = base_width
        center_y = top_edge + (suit_height // 2)

        # ✨ ชดเชยตำแหน่งแนวนอนตาม x_offset
        center_x += config.x_offset

        return SuitRect(x=center_x, y=center_y, width=suit_width, height=suit_height)

    def _smooth(self, x: int, y: int) -> tuple[int, int]:
        if self._smooth_center_x is None:
            self._smooth_center_x = float(x)
            self._smooth_center_y = float(y)
        else:
            alpha = self.smooth_alpha
            self._smooth_center_x = alpha * x + (1 - alpha) * self._smooth_center_x
            self._smooth_center_y = alpha * y + (1 - alpha) * self._smooth_center_y
        return int(self._smooth_center_x), int(self._smooth_center_y)

    @staticmethod
    def _blend(frame: np.ndarray, suit_resized: np.ndarray, rect: SuitRect) -> None:
        h, w = frame.shape[:2]
        cx, cy = rect.x, rect.y
        sw, sh = rect.width, rect.height

        y1 = cy - sh // 2
        y2 = y1 + sh
        x1 = cx - sw // 2
        x2 = x1 + sw

        frame_y1, frame_y2 = max(0, y1), min(h, y2)
        frame_x1, frame_x2 = max(0, x1), min(w, x2)

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

        # --- uint16 Blending เพื่อความรวดเร็ว ---
        if suit_cropped.ndim == 3 and suit_cropped.shape[2] == 4:
            alpha = suit_cropped[:, :, 3:4]
            suit_bgr = suit_cropped[:, :, :3]
            alpha_inv = 255 - alpha

            blended = (suit_bgr.astype(np.uint16) * alpha +
                       roi.astype(np.uint16) * alpha_inv) // 255
            roi[:, :, :] = blended.astype(np.uint8)
        else:
            frame[frame_y1:frame_y2, frame_x1:frame_x2] = suit_cropped[:, :, :3]


class SuitTryOnApp:
    def __init__(self) -> None:  # ✅ แก้: init -> __init__
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"ไม่พบไฟล์โมเดล {MODEL_PATH}")

        base_options = mp.tasks.BaseOptions(model_asset_path=MODEL_PATH)
        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
        )
        self.detector = mp.tasks.vision.PoseLandmarker.create_from_options(options)

        self.all_suits_configs: list[SuitConfig] = SUIT_DATA
        self.active_suits_configs: list[SuitConfig] = []
        self.current_suit_idx: int = 0
        self.current_sex: str | None = None

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

        self.renderer = SuitRenderer(suit_cache)

    def set_user_sex(self, sex: str) -> None:
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

    @property
    def smooth_alpha(self) -> float:
        return self.renderer.smooth_alpha

    @property
    def current_x_offset(self) -> int:
        if not self.active_suits_configs:
            return 0
        return self.active_suits_configs[self.current_suit_idx].x_offset

    def process(self, frame: np.ndarray) -> np.ndarray:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        timestamp_ms = int(time.time() * 1000)
        results = self.detector.detect_for_video(mp_image, timestamp_ms)

        if results.pose_landmarks and self.active_suits_configs:
            config = self.active_suits_configs[self.current_suit_idx]
            frame = self.renderer.render(frame, results.pose_landmarks, config)

        return frame

    def toggle_smoothing(self) -> None:
        self.renderer.toggle_smoothing()

    def adjust_smoothing(self, delta: float) -> None:
        self.renderer.adjust_smoothing(delta)

    def adjust_x_offset(self, delta: int) -> None:
        if not self.active_suits_configs:
            return
        config = self.active_suits_configs[self.current_suit_idx]
        config.x_offset += delta
        logger.info("[%s] x_offset ปรับเป็น: %d", os.path.basename(config.path), config.x_offset)

    def reset_x_offset(self) -> None:
        if not self.active_suits_configs:
            return
        config = self.active_suits_configs[self.current_suit_idx]
        config.x_offset = 0
        logger.info("[%s] x_offset reset เป็น: 0", os.path.basename(config.path))

    def close(self) -> None:
        if hasattr(self, "detector"):
            self.detector.close()

    def switch_suit(self) -> None:
        if not self.active_suits_configs:
            return
        self.current_suit_idx = (self.current_suit_idx + 1) % len(self.active_suits_configs)

    def toggle_sex(self) -> None:
        new_sex = 'F' if self.current_sex == 'M' else 'M'
        self.set_user_sex(new_sex)