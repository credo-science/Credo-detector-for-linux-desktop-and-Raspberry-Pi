# -*- coding: utf-8 -*-
# !/usr/bin/env python
import os
import time
import urllib3
import base64
from internet_functions import registration, old_detection_file, credo_detection, linux_time, credo_ping
import numpy as np
from datetime import datetime
from configparser import ConfigParser
import cv2

os.system("sudo modprobe bcm2835-v4l2")  # command in terminal, that enable pi camera in cv2 module.
# In desktop linux with usb camera unnecessary, but script still work.
local_path = os.path.dirname(os.path.abspath(__file__))
urllib3.disable_warnings()
cfg = ConfigParser()
cfg.read(local_path + '/config.ini')
path = cfg.get('UserPath', 'save_results_path')
test_value = cfg.get('Test', 'test_value')
default_threshold = cfg.get('Test', 'default_threshold')
cam_number = cfg.get('Cam', 'selected_cam')

print("""
Credo-Raspberry v.1.0.0
Author: Tomasz Pluciński


Welcome to the Credo-Linux program.
More information about the credo project 
can be found at: https://credo.science/

""")


def start():
    while True:
        start_app = input("""
1 Start 
2 Registration in Credo 
3 Send old detection files
-- Press h to get help --
 -- Press e to exit --""" + '\n')
        if start_app == "1":
            break
        elif start_app == "h":
            os.system("reset")
            help_file = open(local_path + "/help.text", 'r')
            context = help_file.read()
            print(context)
            continue
        elif start_app == "2":
            os.system("reset")
            registration()
        elif start_app == "3":
            os.system("reset")
            old_detection_file()
            print("Done")
            continue
        elif start_app == "e":
            exit()
        else:
            continue


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


def calibration():
    os.system("reset")
    print("Calibration...")
    cam_read = cv2.VideoCapture(int(cam_number))
    test_number = 0
    max_value = []
    new_x = 0
    new_y = 1
    time.sleep(2)

    while test_number < int(test_value):
        try:
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


calibration()


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


def start_detection():
    global last_ping
    global last_detection_time
    last_ping = linux_time()
    last_detection_time = 0
    cam_read = cv2.VideoCapture(int(cam_number))
    sample_number = sample_save = 0
    print("Start sampling...")
    time.sleep(2)
    os.system("reset")
    while True:
        try:
            time_dat = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
            detection_time = linux_time()
            sample_number += 1
            ret, frame = cam_read.read()
            data = np.array(frame)
            print('\r', "Sample:", sample_number, "|", "Saved", sample_save, "|", "Press Ctrl + c to exit", end='')
            time.sleep(0.000001)
            counter = 0
            xy_coordinates = []
            if np.max(data) >= int(threshold):
                all_coordinate_x = list(np.where(data >= int(threshold))[1])
                all_coordinate_y = list(np.where(data >= int(threshold))[0])
                all_ziped = list(zip(all_coordinate_x,all_coordinate_y))
                all_ziped.sort()
                while counter < len(all_ziped):
                    if len(all_ziped) == 1:
                        xy_coordinates.append(all_ziped[0])
                        break
                    elif counter == 0:
                        xy_coordinates.append(all_ziped[counter])
                        counter += 1
                    elif all_ziped[counter][0] - 10 < all_ziped[counter - 1][0]:
                        counter += 1
                    else:
                        xy_coordinates.append(all_ziped[counter])
                        counter += 1
                multi_detection = 0
                for x, y in xy_coordinates:

                    if x >= 11 and y >= 11:
                        img_crop = data[y-10:y + 10,
                                   x-10:x + 10]
                        r = 50.0 / img_crop.shape[1]
                        dim = (50, int(img_crop.shape[0] * r))
                        sample_save = sample_save + 1
                        if img_crop is None:
                            pass
                        else:
                            print(time_dat, sample_number, x, y,
                                  round(np.average(data), 4), np.max(data),
                                  sep=',', file=open(str(path) + "/Report.txt", "a"))
                            img_zoom = cv2.resize(img_crop, dim, interpolation=cv2.INTER_AREA)
                            gray_img_zoom = cv2.cvtColor(img_zoom, cv2.COLOR_BGR2GRAY)
                            cv2.imwrite(str(path) + "/" + str(time_dat) +
                                        " Sample no. %i:%i.png" % (sample_number,multi_detection), gray_img_zoom)
                        picture = open(str(path) + "/" + str(time_dat) +" Sample no. %i:%i.png"
                                       % (sample_number,multi_detection), 'rb')
                        picture_read = picture.read()
                        base64_picture = str(base64.b64encode(picture_read))[2:]
                        credo_detection(base64_picture, int(x), int(y), detection_time)
                        last_detection_time = linux_time()
                        old_detection_file()
                        multi_detection += 1

                else:
                    pass
            if linux_time() - last_ping >= 600000:
                credo_ping(last_ping, last_detection_time)
                last_ping = linux_time()

        except KeyboardInterrupt:
            cam_read.release()
            exit()


start_detection()
