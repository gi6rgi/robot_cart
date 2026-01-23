import time
from tkinter import NO

import cv2
from picamera2 import Picamera2

SIZE = (3280, 2464)
FORMAT = "RGB888"


class Camera:
    def __init__(self) -> None:
        self.picam2 = Picamera2()

    def start(self):
        config = self.picam2.create_preview_configuration(
            main={"size": SIZE, "format": FORMAT}
        )
        self.picam2.configure(config)
        self.picam2.start()
        time.sleep(1)

    def capture_photo(self, output_path: str) -> str:
        frame = self.picam2.capture_array()
        cv2.imwrite(output_path, frame)
        print(f"Image saved: {output_path}")
        return output_path

    def stop(self) -> None:
        self.picam2.stop()
