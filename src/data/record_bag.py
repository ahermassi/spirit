#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# (C) 2017  Jean Nassar
# Released under MIT
from __future__ import print_function
import argparse
import os

import rosbag

from config import BAG_DIR, ROSBAG_TOPICS


def parse_args():
    parser = argparse.ArgumentParser(description="Record bag files.")
    parser.add_argument("experimenter_id", action="store",
        help="Experimenter ID, as an int.")
    parser.add_argument("experiment_type", action="store",
        help=("Experiment type: 1 for camera alone, 2 for SPIRIT alone, 3 for " 
              "camera and SPIRIT together, and 4 for line-of-sight. Add 5 to "
              "the experiment type to indicate an experiment performed with "
              "obstacles."))
    return parser.parse_args()


def get_next_filename(experiment_type, experimenter_id):
    run_number = 0
    filename_base = os.path.join(BAG_DIR, "experiment-{:d}_user-{:02d}_run-"
        .format(int(experiment_type), int(experimenter_id)))
    while os.path.exists(filename_base + "{:02d}.bag".format(run_number)):
        run_number += 1

    return filename_base + "{:02d}".format(run_number)


def record(arguments):
    rosbag.rosbag_main.record_cmd(arguments)


def main():
    args = parse_args()

    filename = get_next_filename(args.experiment_type, args.experimenter_id)

    arguments = ROSBAG_TOPICS + ["-O", filename]
    record(arguments)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nUser exit")
