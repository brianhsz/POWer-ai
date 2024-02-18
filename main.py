import cv2 as cv
import argparse
import pyfirmata
import math

import StepperLib

from ultralytics import YOLO
from pyfirmata import Arduino, SERVO
from time import sleep


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
    # THIS IS WHAT YOU WANNA HIT #######################################################
    wanna_hit = "Zoa"

    # CONSTANTS ########################################################################
    CALIBRATED_FOCAL_LENGTH = 245
    KNOWN_WIDTH = 35.0

    # Argument parsing #################################################################
    args = get_args()

    cap_device = args.device
    cap_width = args.width
    cap_height = args.height

    # Classification and AI Detection ##################################################
    # Load an official or custom model
    model = YOLO('best.pt')  # Load an official Detect model

    # Perform tracking with the model
    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    classifications = {0: 'SevenUp',
                       1: 'DrPepper',
                       2: 'Pepsi',
                       3: 'Zoa'}
    lockin = False
    width = cap.get(cv.CV_CAP_PROP_FRAME_WIDTH)
    print("THE WIDTH IS: " + str(width))

    # Main #############################################################################
    while True:
        ret, image = cap.read()
        if not ret:
            break

        # DETECTION #
        results = model.predict(image, conf=0.5, imgsz=640, verbose=False, half=True)

        key = cv.waitKey(10)
        if key == 27:  # ESC
            break
        elif key == 107:  # k
            lockin = True

        for result in results:
            for box in result.boxes:
                pixel_width = float(box.xyxy[0][2]) - float(box.xyxy[0][0])
                if wanna_hit == classifications[int(box.cls[0])] and lockin:
                    distance = distance_to_camera(KNOWN_WIDTH, CALIBRATED_FOCAL_LENGTH, pixel_width)
                    ratio = pixel_width/KNOWN_WIDTH
                    mid_point = box.xyxy[0][0] + pixel_width / 2
                    point_to_can(mid_point, distance, distance * ratio)
                    print("TARGET SPOTTED " + str(distance) + " AWAY")
                    lockin = False

        annotated_frame = results[0].plot()

        cv.imshow('Distance Detection', annotated_frame)

    cv.destroyAllWindows()


def rotate_servo(pin, angle):
    board.digital[pin].write(angle)
    sleep(0.015)


# make it so take distance to create angle
def get_shot_angle(distance):
    CALIBRATION_CONST = 90
    degrees = 45 * (distance / CALIBRATION_CONST)
    adjust = 180 - degrees
    rotate_servo(5, adjust)


def point_to_can(x_pos, dist, dist_in_pixels):
    dist_from_mid = 900 - x_pos

    angle = math.degrees(math.atan(dist_from_mid/dist_in_pixels))
    print("XPOS")
    print(x_pos)

    print("DISTANCE FROM MID")
    print(dist_from_mid)

    print("DISTANCE FROM CAM")
    print(dist_in_pixels)

    print(angle)

    motor.step(angle * DEGREE_TO_STEP_CONV)
    board.digital[5].mode = SERVO

    get_shot_angle(dist)
    sleep(10)
    recalibrate_servo()
    return True


def recalibrate_servo():
    board.digital[5].mode = SERVO
    rotate_servo(5, 180)


# MAIN PROGRAM ############################################################
board = Arduino('COM3')
DEGREE_TO_STEP_CONV = (2038 * 2) / 360
reader = pyfirmata.util.Iterator(board)  # reads inputs of the circuit
reader.start()

motor = StepperLib.Stepper(2038, board, reader, 11, 10, 9, 8)
motor.set_speed(100000)

# point_to_can(900,30,460)
main()

recalibrate_servo()
