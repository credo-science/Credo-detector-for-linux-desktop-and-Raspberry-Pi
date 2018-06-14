# -*- coding: utf-8 -*-
# !/usr/bin/env python
import os
import time
import numpy as np
from datetime import datetime
from configparser import ConfigParser
import cv2  # CV2 - Important module, installation on raspberry zero take 13 hours
from cv2 import CAP_PROP_FPS
from cv2 import CAP_PROP_BRIGHTNESS

# command in terminal, that enable pi camera in cv2 module.
# In desktop linux with usb camera unnecessary, but script still work.
os.system("sudo modprobe bcm2835-v4l2")
local_path = os.path.dirname(os.path.abspath(__file__))
cfg = ConfigParser()
cfg.read(local_path + '/config.ini')
path = cfg.get('UserPath', 'save_results_path')
test_value = cfg.get('Test', 'test_value')
default_threshold = cfg.get('Test', 'default_threshold')
cam_number = cfg.get('Cam', 'selected_cam')

print("""
Credo-Raspberry
Author: Tomasz Pluciński




Welcome to the Credo-Linux program.
More information about the credo project 
can be found at: https://credo.science/

""")
print("")
print("")


def start():
    start_app = input("Press s to start or h to get help")
    if start_app == "s":
        pass
    elif start_app == "h":
        help_file = open(local_path + "/help.text", 'r')
        context = help_file.read()
        print(context)
        start()
    else:
        start()


start()


def samples_path():
    path_exist = os.path.isdir(path)
    if path_exist is False:
        print("Path does not exist")
        time.sleep(2)
        exit()


samples_path()

print("\n")
print("\n")
os.system("reset")
print("Calibration...")
cam_read = cv2.VideoCapture(int(cam_number))
cam_read.set(CAP_PROP_FPS, 30)
cam_read.set(CAP_PROP_BRIGHTNESS, 0.5)
sample_number = sample_save = test_number = 0
max_value = []
new_x = 0
new_y = 1
font = cv2.FONT_HERSHEY_SIMPLEX
time.sleep(2)

while test_number < int(test_value):
    try:
        time_dat = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
        test_number += 1
        return_value, image = cam_read.read()
        test_data = np.array(image)
        test_data_crop = test_data[new_x + 10:new_x - 10, new_y + 10:new_y - 10]
        max_value.append(np.max(test_data_crop))
        print('\r', "Test no.:", test_number, "/", test_value,
              "Max:", np.max(test_data_crop),
              "Average:", round(np.average(test_data_crop), 4),
              "Exit ctrl+c", end='')
        time.sleep(1)

    except KeyboardInterrupt:
        cam_read.release()
        exit()

print('\n')
print("Calibration completed")
time.sleep(1)
avg_max_value = (sum(max_value) / len(max_value))
print("\n")
print("Maximum value: " + str(max(max_value)))
print("Average of maximum values: " + str(avg_max_value))
print("\n")
time.sleep(1)


# Calibration show max value and average of max value. In my opinion is unnecessary when we want catch bright particles.
# I usually set in config file calibration value as 1 and then threshold as 60.

def threshold_choice():
    global threshold
    select_threshold = input(
        """Choose the sampling threshold:
            1: Default threshold
            2: Custom option""")
    if select_threshold == "1":
        threshold = default_threshold
    elif select_threshold == "2":
        if True:
            try:
                threshold = int(input("Enter a value from the range 0-255"))
            except ValueError:
                print("Incorrect value")
                time.sleep(1)
                threshold_choice()
        if 0 < int(threshold) < 255:
            pass
        else:
            print("Incorrect value")
            time.sleep(1)
            threshold_choice()
    else:
        threshold_choice()


threshold_choice()

print("Start sampling...")
time.sleep(2)
os.system("reset")
while True:
    try:
        time_dat = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
        sample_number += 1
        new_x = new_y = 0
        ret, frame = cam_read.read()
        data = np.array(frame)
        print('\r' + str(sample_number) + " | " + str(sample_save), end='')
        time.sleep(0.000001)
        if np.max(data) >= int(threshold):
            all_coordinate_x = (np.where(data == np.max(data))[1])
            all_coordinate_y = (np.where(data == np.max(data))[0])
            chosen_coordinate_x = all_coordinate_x[0] - 5
            chosen_coordinate_y = all_coordinate_y[0] - 5
            if chosen_coordinate_x >= 11 and chosen_coordinate_y >= 11:
                img_crop = data[chosen_coordinate_y:chosen_coordinate_y + 10,
                                chosen_coordinate_x:chosen_coordinate_x + 10]
                r = 500.0 / img_crop.shape[1]
                dim = (500, int(img_crop.shape[0] * r))
                sample_save = sample_save + 1
                if img_crop is None:
                    pass
                else:
                    print(time_dat, sample_number, chosen_coordinate_x, chosen_coordinate_y,
                          round(np.average(data), 4), np.max(data),
                          sep=',', file=open(str(path) + "/Report.txt", "a"))
                    img_zoom = cv2.resize(img_crop, dim, interpolation=cv2.INTER_AREA)
                    cv2.putText(img_zoom, "x: " + str(chosen_coordinate_x) + " " +
                                "y: " + str(chosen_coordinate_y) + " " +
                                'Average: ' + str(round(np.average(img_zoom), 4)) +
                                " " + "Max: " + str(np.max(img_zoom)), (10, 490), font, 0.5,
                                (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.putText(data, "x: " + str(chosen_coordinate_x) + " " + "y: " + str(chosen_coordinate_y) +
                                " " + "Average: " + str(round(np.average(data), 4)) + " " + "Max: " +
                                str(np.max(data)), (10, 450), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                    gray_data = cv2.cvtColor(data, cv2.COLOR_BGR2GRAY)
                    cv2.rectangle(gray_data, (chosen_coordinate_x, chosen_coordinate_y),
                                  (chosen_coordinate_x + 10, chosen_coordinate_y + 10), (255, 255, 255), 1)
                    gray_img_zoom = cv2.cvtColor(img_zoom, cv2.COLOR_BGR2GRAY)
                    cv2.imwrite(str(path) + "/" + str(time_dat) + " Picture no. %i.jpeg" % sample_number, gray_data)
                    cv2.imwrite(str(path) + "/" + str(time_dat) + " Sample no. %i.jpeg" % sample_number, gray_img_zoom)
                    time.sleep(1)
            else:
                pass

    except KeyboardInterrupt:
        cam_read.release()
        exit()
