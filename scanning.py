import os
import cv2
import time
import threading
import winsound
from pyzbar.pyzbar import decode, ZBarSymbol
from database import Matching_QR

os.environ["ZBAR_LOG_LEVEL"] = "ERROR"


class Scan:
    def __init__(self):
        self.info = Matching_QR()
        self.cam = cv2.VideoCapture(0)

        self.last_scan_time = 0
        self.SCAN_DELAY = 1  # seconds

        self.result = None
        self.detected_time = None

        self.is_fetching = False
        self.last_barcode = None
        self.sound_played = False

        self.lock = threading.Lock()

    def fetch_result(self, barcode_data):
        result = self.info.find_info(barcode=barcode_data)

        with self.lock:
            if result is not None:
                self.result = result
                self.detected_time = time.time()
            self.is_fetching = False

    def get_fullname(self):
        try:
            if self.result and len(self.result) > 0:
                return self.result[0].get("name", "Unknown")
        except (TypeError, KeyError, IndexError):
            pass
        return "Unknown"

    def start_scanning(self):
        while True:
            success, frame = self.cam.read()
            if not success:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            decoded_objects = decode(gray, symbols=[ZBarSymbol.CODE128])
            current_time = time.time()

            for obj in decoded_objects:
                x, y, w, h = obj.rect
                x -= 5
                y -= 5
                w += 10
                h += 10

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                barcode_data = obj.data.decode("utf-8").strip()

                # prevent duplicate rapid scans of the same barcode
                if barcode_data == self.last_barcode:
                    continue

                if current_time - self.last_scan_time >= self.SCAN_DELAY:
                    if not self.is_fetching:
                        self.is_fetching = True
                        self.last_barcode = barcode_data
                        self.last_scan_time = current_time

                        threading.Thread(
                            target=self.fetch_result,
                            args=(barcode_data,),
                            daemon=True
                        ).start()

            # play sound only once after valid detection
            if self.detected_time:
                
                if time.time() - self.detected_time >= 3:
                    # 🔊 play sound ON EXIT
                    winsound.Beep(1000, 400)
                    break

            # display result on screen
            if self.result:
                fullname = self.get_fullname()

                cv2.putText(
                    frame,
                    "Authentication confirmed",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"Name: {fullname}",
                    (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

            cv2.imshow("OurQr_Code_Scanner", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    scanner = Scan()
    scanner.start_scanning()