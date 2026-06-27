# main.py
import logging
import time
import cv2
import os
import numpy as np
from tryon_engine import SuitTryOnApp
from config import DEFAULT_SEX

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
)


class HUDRenderer:
    """HUD แบบ Multi-Page: กด H เพื่อสลับหน้า"""

    def __init__(self):
        self.current_page = 0          # 0 = Basic, 1 = Tuning
        self.total_pages = 2

    def next_page(self):
        self.current_page = (self.current_page + 1) % self.total_pages
        page_name = ["Basic", "Tuning"][self.current_page]
        logging.info("HUD Page: %s (%d/%d)", page_name, self.current_page + 1, self.total_pages)

    def _draw_text_with_outline(self, frame: np.ndarray, text: str, pos: tuple[int, int],
                                 font_scale: float, fill_color: tuple[int, int, int],
                                 outline_color: tuple[int, int, int] = (0, 0, 0),
                                 thickness: int = 2) -> None:
        """✨ วาดข้อความพร้อมขอบดำ (outline) เพื่อให้เห็นชัดทุกพื้นหลัง"""
        x, y = pos
        # วาดขอบดำ 8 ทิศทาง
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                cv2.putText(frame, text, (x + dx, y + dy),
                            cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                            outline_color, thickness + 1, cv2.LINE_AA)
        # วาดสีสดทับ
        cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                    fill_color, thickness, cv2.LINE_AA)

    def draw(self, frame: np.ndarray, app: SuitTryOnApp, fps: float) -> None:
        h, w, _ = frame.shape

        # --- FPS Counter มุมบนซ้าย (สีเหมือนเดิม) ---
        fps_color = (0, 255, 0) if fps >= 25 else ((0, 255, 255) if fps >= 15 else (0, 0, 255))
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, fps_color, 2)

        # --- Page Indicator มุมบนขวา (✨ เปลี่ยนสี + ขยับขวา + มี outline) ---
        page_name = ["Basic", "Tuning"][self.current_page]
        page_text = f"[H] Page: {page_name} ({self.current_page + 1}/{self.total_pages})"
        # ✨ ขยับขวาจาก w-350 เป็น w-280 (ขยับเข้าไปในจออีก 70px)
        # ✨ ใช้สีส้มสด (0, 165, 255) พร้อม outline ดำ → เห็นชัดทุกพื้นหลัง
        self._draw_text_with_outline(
            frame, page_text, (w - 280, 30),
            font_scale=0.65,
            fill_color=(0, 165, 255),     # สีส้มสด (BGR)
            outline_color=(0, 0, 0),      # ขอบดำ
            thickness=2
        )

        # --- วาด HUD ตามหน้าปัจจุบัน ---
        if self.current_page == 0:
            self._draw_basic_page(frame, app)
        else:
            self._draw_tuning_page(frame, app)

    def _draw_basic_page(self, frame: np.ndarray, app: SuitTryOnApp) -> None:
        """หน้า Basic: ปุ่มหลัก + สถานะชุด"""
        h, w, _ = frame.shape

        roi = frame[h - 80:h, :]
        overlay = np.zeros_like(roi)
        cv2.addWeighted(overlay, 0.5, roi, 0.5, 0, roi)

        current = app.active_suits_configs[app.current_suit_idx] if app.active_suits_configs else None
        suit_name = os.path.basename(current.path) if current else "N/A"
        suit_sex = current.sex if current else "-"

        cv2.putText(frame,
                    "[S] Switch  [F] Sex  [P] Save  [Q] Quit  |  [H] Tuning Page",
                    (10, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.putText(frame,
                    f"Suit: {suit_name} | Sex: {suit_sex} | No.{app.current_suit_idx + 1}/{len(app.active_suits_configs)}",
                    (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

    def _draw_tuning_page(self, frame: np.ndarray, app: SuitTryOnApp) -> None:
        """หน้า Tuning: Smooth + Offset + Stretch"""
        h, w, _ = frame.shape

        roi = frame[h - 140:h, :]
        overlay = np.zeros_like(roi)
        cv2.addWeighted(overlay, 0.5, roi, 0.5, 0, roi)

        smooth_status = "ON" if app.smoothing_enabled else "OFF"
        x_offset = app.current_x_offset
        y_offset = app.current_y_offset
        stretch_x = app.current_stretch_x
        stretch_y = app.current_stretch_y

        cv2.putText(frame,
                    f"Smooth: {smooth_status} (alpha={app.smooth_alpha:.2f})  |  [+/-] Alpha  [T] Toggle",
                    (10, h - 115), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cv2.putText(frame,
                    f"Offset: X={x_offset:+d}px  Y={y_offset:+d}px  |  [ ] X  [I/K] Y  [9/0] Reset",
                    (10, h - 85), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 255, 180), 1)
        cv2.putText(frame,
                    f"Stretch: X={stretch_x:.2f}  Y={stretch_y:.2f}  |  [A/D] Width  [W/X] Height  [R] Reset",
                    (10, h - 55), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 200, 100), 1)
        cv2.putText(frame,
                    "[H] Back to Basic Page",
                    (10, h - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

    @staticmethod
    def save_screenshot(frame: np.ndarray):
        os.makedirs('captures', exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"captures/tryon_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        logging.info("Saved: %s", filename)


def main():
    app = None
    cap = None
    try:
        app = SuitTryOnApp()
        # ไม่ต้องเรียก set_user_sex แล้ว เพราะ __init__ เรียกให้แล้ว

        cv2.namedWindow('Virtual Try-On', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Virtual Try-On', 960, 720)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.error("ไม่สามารถเปิดกล้องได้")
            return

        hud = HUDRenderer()

        prev_time = time.time()
        fps_display = 0.0
        EMA_ALPHA = 0.1
        consecutive_failures = 0
        MAX_FAILURES = 30

        KEY_MAP = {
            ord('s'): app.switch_suit,
            ord('f'): app.toggle_sex,
            ord('t'): app.toggle_smoothing,
            ord('+'): lambda: app.adjust_smoothing(+0.1),
            ord('='): lambda: app.adjust_smoothing(+0.1),
            ord('-'): lambda: app.adjust_smoothing(-0.1),
            ord('_'): lambda: app.adjust_smoothing(-0.1),
            # X-Offset
            ord('['): lambda: app.adjust_x_offset(-1),
            ord(']'): lambda: app.adjust_x_offset(+1),
            ord('{'): lambda: app.adjust_x_offset(-5),
            ord('}'): lambda: app.adjust_x_offset(+5),
            ord('0'): app.reset_x_offset,
            # ✨ Y-Offset
            ord('i'): lambda: app.adjust_y_offset(-1),    # เลื่อนขึ้น 1px
            ord('k'): lambda: app.adjust_y_offset(+1),    # เลื่อนลง 1px
            ord('I'): lambda: app.adjust_y_offset(-5),    # เลื่อนขึ้น 5px (Shift+I)
            ord('K'): lambda: app.adjust_y_offset(+5),    # เลื่อนลง 5px (Shift+K)
            ord('9'): app.reset_y_offset,                 # Reset y_offset
            # ✨ STRETCH
            ord('a'): lambda: app.adjust_stretch_x(-0.05),
            ord('d'): lambda: app.adjust_stretch_x(+0.05),
            ord('w'): lambda: app.adjust_stretch_y(+0.05),
            ord('x'): lambda: app.adjust_stretch_y(-0.05),
            ord('r'): app.reset_stretch,
            # ✨ HUD Page
            ord('h'): hud.next_page,
        }

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                consecutive_failures += 1
                if consecutive_failures >= MAX_FAILURES:
                    logging.error("กล้องหลุดถาวร ปิดโปรแกรม")
                    break
                time.sleep(0.05)
                continue
            consecutive_failures = 0

            curr_time = time.time()
            delta = curr_time - prev_time
            fps_raw = 1.0 / delta if delta > 0 else 0.0
            prev_time = curr_time
            fps_display = (EMA_ALPHA * fps_raw) + ((1 - EMA_ALPHA) * fps_display)

            frame = app.process(frame)
            hud.draw(frame, app, fps_display)
            cv2.imshow('Virtual Try-On', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('p'):
                HUDRenderer.save_screenshot(frame)
            else:
                action = KEY_MAP.get(key)
                if action:
                    action()

    except (FileNotFoundError, RuntimeError) as e:
        logging.error(e)
    finally:
        if app:
            app.close()
        if cap and cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()