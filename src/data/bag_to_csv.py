#!/usr/bin/env python
from __future__ import print_function
import glob
import logging
import os

import rosbag_pandas
import tqdm

from config import BAG_DIR, CSV_DIR, CSV_TOPICS, CSV_COLUMN_NAMES


if not os.path.exists(CSV_DIR):
    os.makedirs(CSV_DIR)


def load_bag(filename, include=CSV_TOPICS, column_names=CSV_COLUMN_NAMES):
    df = rosbag_pandas.bag_to_dataframe(filename, include=include)
    pad_bag(df)
    rename_columns(df, column_names)
    normalize_columns(df)
    return df


def pad_bag(df):
    df.fillna(method="pad", inplace=True)
    df.fillna(method="backfill", inplace=True)


def rename_columns(df, column_names):
    df.columns = column_names


def normalize_columns(df):
    df["xn"] = df.x - df.x[0]
    df["yn"] = df.y - df.y[0]


def base_name(filename):
    return os.path.splitext(os.path.basename(filename))[0]


def convert_to_csv(bag_filename, overwrite=False):
    base = base_name(bag_filename)
    csv_filename = os.path.join(CSV_DIR, base + ".csv")
    exists = os.path.exists(csv_filename)
    if overwrite or not exists:
        logging.info("Converting {}".format(base))
        df = load_bag(bag_filename)
        df.to_csv(csv_filename, index_label="time")
    else:
        logging.info("Ignoring {}".format(base))


def batch_convert():
    bag_filenames = glob.glob(os.path.join(BAG_DIR, "*.bag"))
    for bag_filename in tqdm.tqdm(bag_filenames):
        convert_to_csv(bag_filename)


if __name__ == "__main__":
    batch_convert()

