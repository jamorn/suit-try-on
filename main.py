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
    @staticmethod
    def draw(frame: np.ndarray, app: SuitTryOnApp, fps: float) -> None:
        h, w, _ = frame.shape

        # แสดง FPS มุมบนซ้าย
        fps_color = (0, 255, 0) if fps >= 25 else ((0, 255, 255) if fps >= 15 else (0, 0, 255))
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, fps_color, 2)

        # แถบพื้นหลังดำโปร่งแสงด้านล่าง
        roi = frame[h - 120:h, :]
        overlay = np.zeros_like(roi)
        cv2.addWeighted(overlay, 0.5, roi, 0.5, 0, roi)

        current = app.active_suits_configs[app.current_suit_idx] if app.active_suits_configs else None
        suit_name = os.path.basename(current.path) if current else "N/A"
        suit_sex = current.sex if current else "-"
        smooth_status = "ON" if app.smoothing_enabled else "OFF"
        x_offset = app.current_x_offset

        cv2.putText(frame,
                    f"[S] Switch  [F] Sex  [T] Smooth:{smooth_status}  [+/-] Alpha:{app.smooth_alpha:.2f}  [P] Save  [Q] Quit",
                    (10, h - 95), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cv2.putText(frame,
                    f"Suit: {suit_name} | Sex: {suit_sex} | No.{app.current_suit_idx + 1}/{len(app.active_suits_configs)}",
                    (10, h - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv2.putText(frame,
                    f"Smoothing: {smooth_status} (alpha={app.smooth_alpha:.2f}) | X-Offset: {x_offset:+d}px",
                    (10, h - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame,
                    f"Adjust X: [ ] -1px  [ ] +1px  [{{ ] -5px  [}} ] +5px  [0] Reset",
                    (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 255, 180), 1)

    @staticmethod
    def save_screenshot(frame: np.ndarray):
        os.makedirs('captures', exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"captures/tryon_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        logging.info("📸 บันทึกภาพ: %s", filename)


def main():
    app = None
    cap = None
    try:
        app = SuitTryOnApp()
        app.set_user_sex(DEFAULT_SEX)

        cv2.namedWindow('Virtual Try-On', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Virtual Try-On', 960, 720)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.error("ไม่สามารถเปิดกล้องได้")
            return

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
            ord('['): lambda: app.adjust_x_offset(-1),
            ord(']'): lambda: app.adjust_x_offset(+1),
            ord('{'): lambda: app.adjust_x_offset(-5),
            ord('}'): lambda: app.adjust_x_offset(+5),
            ord('0'): app.reset_x_offset,
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
            HUDRenderer.draw(frame, app, fps_display)
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


if __name__ == "__main__":  # ✅ แก้: name == "main" -> __name__ == "__main__"
    main()