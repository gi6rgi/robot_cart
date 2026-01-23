import os

import cv2

# TODO: meditate on Servo class implementation
from src import models, servo
from src.camera import Camera
from src.config import settings
from src.llm import invoke


def app_setup() -> None:
    for folder_name in [
        settings.app.action_logs_dir,
        settings.app.image_logs_dir,
    ]:
        os.makedirs(folder_name)


def explore(
    camera: Camera,
    action_number: int,
    journey_notes: list[str],
    last_actions: list[models.Action],
) -> None:
    # Temp research implementation.
    photo_path = f"{settings.app.image_logs_dir}/{action_number}.png"
    current_photo_path = camera.capture_photo(photo_path)
    resized_photo_path = resize_image(current_photo_path)

    llm_response = invoke(
        request=models.InvokeRequest(
            journey_notes=journey_notes,
            last_actions=last_actions,
            image_path=resized_photo_path,
        )
    )
    print(llm_response)


def resize_image(path: str, max_side: int = 1920, output_path: str | None = None) -> str:
    image = cv2.imread(path)
    if image is None:
        raise ValueError(f"Unable to read image at {path}")

    height, width = image.shape[:2]
    current_max = max(height, width)
    if current_max <= max_side:
        return path

    scale = max_side / current_max
    new_width = max(1, int(width * scale))
    new_height = max(1, int(height * scale))
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    if output_path is None:
        root, ext = os.path.splitext(path)
        output_path = f"{root}_small{ext}"

    cv2.imwrite(output_path, resized)
    return output_path


def run(camera: Camera):
    journey_notes: list[str] = []
    last_actions: list[models.Action] = []

    explore(
        camera=camera,
        action_number=1,
        journey_notes=journey_notes,
        last_actions=last_actions,
    )


def main() -> None:
    app_setup()

    camera = Camera()
    camera.start()


if __name__ == "__main__":
    main()
