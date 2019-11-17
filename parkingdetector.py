
import numpy as np
import cv2


class ParkingDetector:
    def __init__(self):
        self.lower_yellow = np.array([0, 130, 130], dtype="uint8")
        self.upper_yellow = np.array([120, 255, 255], dtype="uint8")
        self.parking_spaces = [{"id": 0, "x": 0, "y": 0, "empty": True}]
        self.calibrated = False
        self.calibrating = False

    def detect_empty_spaces(self, img):

        if not(self.calibrated):
            print(
                "The Parking Detector is not calibrated yet. Please use init_calibrate_parking_spaces(img) & confirm_calibration() in order to calibrate the detector")
            return
        image = cv2.imread(img)
        resized = cv2.resize(image, None, fx=0.5, fy=0.5,
                             interpolation=cv2.INTER_AREA)
        blurred = cv2.GaussianBlur(resized, (5, 5), 0)

        # create mask of yellow objects
        mask = cv2.inRange(blurred, self.lower_yellow, self.upper_yellow)
        mask = cv2.erode(mask, None, iterations=1)

        # detect yellow circles in the mask
        yellow_circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1, 50,
                                          param1=200, param2=10, minRadius=0, maxRadius=0)
        yellow_circles = np.array(np.around(yellow_circles), dtype="uint16")

        for ps in self.parking_spaces:
            x_upper_th = ps["x"] + 7
            y_upper_th = ps["y"] + 7
            x_lower_th = ps["x"] - 7
            y_lower_th = ps["y"] - 7
            detected_match = 0
            for yc in yellow_circles:
                if (x_lower_th < yc[0] < x_upper_th) & (y_lower_th < yc[1] < y_upper_th):
                    detected_match += 1

            ps["empty"] = True if detected_match > 0 else False

    def init_calibrate_parking_spaces(self, img):
        self.calibrated = False
        self.calibrating = True
        self.parking_spaces = []

        image = cv2.imread(img)
        resized = cv2.resize(image, None, fx=0.5, fy=0.5,
                             interpolation=cv2.INTER_AREA)
        blurred = cv2.GaussianBlur(resized, (5, 5), 0)

        # create mask of yellow objects
        mask = cv2.inRange(blurred, self.lower_yellow, self.upper_yellow)
        mask = cv2.erode(mask, None, iterations=1)
        # detect yellow circles in the mask
        yellow_circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1, 50,
                                          param1=200, param2=10, minRadius=0, maxRadius=0)
        yellow_circles = np.array(np.around(yellow_circles), dtype="uint16")
        curr_circle = 0
        for yc in yellow_circles[0]:
            cv2.circle(resized, (yc[0], yc[1]), yc[2], 0, 2)
            self.parking_spaces.append({
                "id": curr_circle, "x": yc[0], "y": yc[1], "empty": True})
            curr_circle += 1

        # write image to folder
        cv2.imwrite("/home/images/calibration_image.jpg", resized)
        return resized

    def confirm_calibration(self):
        if self.calibrating:
            self.calibrated = True
            self.calibrating = False
            return True
        return False

    def get_parking_spaces(self):
        if not(self.calibrated):
            print(
                "The Parking Detector is not calibrated yet. Please use init_calibrate_parking_spaces(img) & confirm_calibration() in order to calibrate the detector")
            return None
        res = []
        for ps in self.parking_spaces:
            res.append({"id": ps["id"], "empty": ps["empty"]})
        return res
