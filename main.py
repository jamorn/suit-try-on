# main.py
import logging
import cv2
import os
import mediapipe as mp
from tryon_engine import SuitTryOnApp
from config import DEFAULT_SEX

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
)


def main():
    try:
        app = SuitTryOnApp()
    except (FileNotFoundError, RuntimeError) as e:
        logging.error(e)
        return

    app.set_user_sex(DEFAULT_SEX)

    cv2.namedWindow('Virtual Try-On', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Virtual Try-On', 960, 720)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        cap.release()
        logging.error("ไม่สามารถเปิดกล้องได้")
        return

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                logging.warning("ไม่สามารถอ่านเฟรมจากกล้องได้")
                break

            # แปลงสีสำหรับ MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            # ตรวจจับ
            results = app.detector.detect(mp_image)

            if results.pose_landmarks:
                frame = app.overlay_suit(frame, results.pose_landmarks)

            # --- OSD: แสดง Key Guide และสถานะ ---
            h, w, _ = frame.shape
            overlay = frame.copy()
            # พื้นหลังโปร่งใสด้านล่าง
            cv2.rectangle(overlay, (0, h - 80), (w, h), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

            current = app.active_suits_configs[app.current_suit_idx] if app.active_suits_configs else None
            if current:
                suit_name = os.path.basename(current.path)
                suit_sex = current.sex
            else:
                suit_name, suit_sex = "N/A", "-"
            smooth_status = "ON" if app.smoothing_enabled else "OFF"

            cv2.putText(frame, f"[S] Switch Suit  [F] Change Sex  [T] Smooth: {smooth_status}  [Q] Quit",
                        (10, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Suit: {suit_name} | Sex: {suit_sex} | No.{app.current_suit_idx + 1}/{len(app.active_suits_configs)}",
                        (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            cv2.imshow('Virtual Try-On', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                app.switch_suit()
            elif key == ord('f'):
                new_sex = 'F' if app.current_sex == 'M' else 'M'
                app.set_user_sex(new_sex)
            elif key == ord('t'):
                app.toggle_smoothing()

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

