import cv2 as cv
import argparse

from ultralytics import YOLO
from pyfirmata import Arduino
import time


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--width", help='cap width', type=int, default=3000)
    parser.add_argument("--height", help='cap height', type=int, default=1500)

    parser.add_argument('--use_static_image_mode', action='store_true')
    parser.add_argument("--min_detection_confidence",
                        help='min_detection_confidence',
                        type=float,
                        default=0.7)
    parser.add_argument("--min_tracking_confidence",
                        help='min_tracking_confidence',
                        type=int,
                        default=0.5)

    args = parser.parse_args()

    return args


def distance_to_camera(known_width, focal_length, per_width):
    return (known_width * focal_length) / per_width


def main():
    CALIBRATED_FOCAL_LENGTH = 1670
    KNOWN_WIDTH = 35.0

    # Argument parsing #################################################################
    args = get_args()

    cap_device = args.device
    cap_width = args.width
    cap_height = args.height

    use_static_image_mode = args.use_static_image_mode
    min_detection_confidence = args.min_detection_confidence
    min_tracking_confidence = args.min_tracking_confidence

    # Load an official or custom model
    model = YOLO('best.pt')  # Load an official Detect model

    # Perform tracking with the model

    cap = cv.VideoCapture(cap_device)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    while True:
        # CAMERA #
        ret, image = cap.read()
        if not ret:
            break
        img = cv.flip(image, 1)  # Mirror display

        # DETECTION #
        results = model.predict(img, conf=0.5, verbose=False)

        distances = []

        for result in results:
            for box in result.boxes.xyxy:
                pixel_width = float(box[2])-float(box[0])

                distance = distance_to_camera(KNOWN_WIDTH, CALIBRATED_FOCAL_LENGTH, pixel_width)

        annotated_frame = results[0].plot()

        cv.imshow('distance detection', annotated_frame)
        key = cv.waitKey(10)
        if key == 27:  # ESC
            break

    cv.destroyAllWindows()


# board = Arduino('COM3')
# while True:
#     board.digital[13].write(1)
#     time.sleep(1)
#     board.digital[13].write(0)
#     time.sleep(1)

main()