from picamera2 import Picamera2
import time
import cv2

SIZE = (3280, 2464)
FORMAT = "RGB888"

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": SIZE, "format": FORMAT})
picam2.configure(config)

picam2.start()
time.sleep(1)

frame = picam2.capture_array()
frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

filename = "frame.png"
cv2.imwrite(filename, frame_bgr)
print(f"Saved: {filename}")

picam2.stop()

