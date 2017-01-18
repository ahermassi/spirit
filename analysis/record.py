#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# (C) 2017  Jean Nassar
# Released under MIT
from __future__ import print_function
import os
import sys

import rosbag

FOLDER = "bagfiles"
ROSBAG_TOPICS = [
    "/ardrone/ground_pose",
    "/ardrone/imu",
    "/ardrone/navdata",
    "/ardrone/odometry",
    "/ardrone/past_image",
    "/ardrone/past_pose",
    "/ardrone/pose",
    "/ardrone/slow_image_raw",
    "/ardrone/tracked",
    "/ardrone/arrived",
    "/rosout",
    "/rosout_agg",
]


def parse_args():
    if len(sys.argv) != 3:
        print("Please have experiment type (0 for no SPIRIT, 1 for SPIRIT only,"
              " 2 for both camera and SPIRIT), experimenter id (0 to 99), as "
              "arguments.")
        sys.exit(1)
    _, experiment_type, experimenter_id = sys.argv
    return experiment_type, experimenter_id


def get_filename(experiment_type, experimenter_id):
    run_number = 0
    filename_base = os.path.join(FOLDER, "experiment-{:d}_user-{:02d}_run-"
        .format(int(experiment_type), int(experimenter_id)))
    while os.path.exists(filename_base + "{:02d}.bag".format(run_number)):
        run_number += 1

    return filename_base + "{:02d}".format(run_number)


def record(arguments):
    rosbag.rosbag_main.record_cmd(arguments)


def main():
    experiment_type, experimenter_id = parse_args()
    filename = get_filename(experiment_type, experimenter_id)
    arguments = ROSBAG_TOPICS + ["-O", filename]
    record(arguments)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nUser exit")
