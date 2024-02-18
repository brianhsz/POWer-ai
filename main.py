import cv2 as cv
import argparse

from ultralytics import YOLO
import pyfirmata
from pyfirmata import Arduino, SERVO
from time import sleep
import StepperLib
import math


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
    # THIS IS WHAT YOU WANNA HIT ##########
    WANNA_HIT = '7up'

    CALIBRATED_FOCAL_LENGTH = 230
    KNOWN_WIDTH = 35.0

    # Argument parsing #################################################################
    args = get_args()

    cap_device = args.device
    cap_width = args.width
    cap_height = args.height

    # Load an official or custom model
    model = YOLO('best.pt')  # Load an official Detect model

    # Perform tracking with the model
    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    classifications = {0: '7up',
                       1: 'DrPepper',
                       2: 'Pepsi',
                       3: 'Zoa'}

    while True:
        ret, image = cap.read()
        if not ret:
            break
        img = cv.flip(image, 1)  # Mirror display

        # DETECTION #
        results = model.predict(img, conf=0.5, imgsz = 640, verbose=False, half=True)

        for result in results:
            for box in result.boxes:
                pixel_width = float(box.xyxy[0][2])-float(box.xyxy[0][0])
                if WANNA_HIT == classifications[int(box.cls[0])]:
                    distance = distance_to_camera(KNOWN_WIDTH, CALIBRATED_FOCAL_LENGTH, pixel_width)
                    # point_to_can(float(box.xyxy[0][0]), distance)
                    print("TARGET SPOTTED " + str(distance) + " AWAY")

        annotated_frame = results[0].plot()

        cv.imshow('distance detection', annotated_frame)
        key = cv.waitKey(10)
        if key == 27:  # ESC
            break

    cv.destroyAllWindows()


def rotate_servo(pin, angle):
    board.digital[pin].write(angle)
    sleep(0.015)


# make it so take distance to create angle
def get_shot_angle(distance):
    degrees=0 #implement later
    adjust = 180-degrees
    rotate_servo(5, adjust)


def point_to_can(x_pos,dist):
    # implement this later
    DEGREE_TO_STEP_CONV = (2038 * 2) / 360
    board = Arduino('COM3')
    reader = pyfirmata.util.Iterator(board)  # reads inputs of the circuit
    reader.start()

    motor = StepperLib.Stepper(2038, board, reader, 11, 10, 9, 8)
    motor.set_speed(100000)

    motor.step(90 * DEGREE_TO_STEP_CONV)

    get_shot_angle(dist)
    return True


main()

