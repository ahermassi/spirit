BAG_DIR = "../data/raw"
CSV_DIR = "../data/interim"

ROSBAG_TOPICS = [
    "/ardrone/ground_pose",
    "/ardrone/imu",
    "/ardrone/navdata",
    # "/ardrone/odometry",
    # "/ardrone/past_image",
    "/ardrone/past_pose",
    "/ardrone/pose",
    # "/ardrone/slow_image_raw",
    "/ardrone/tracked",
    "/ardrone/arrived",
    # "/rosout",
    # "/rosout_agg",
]

CSV_TOPICS = [
    "/ardrone/arrived",
    "/ardrone/ground_pose",
    "/ardrone/pose",
]

CSV_COLUMN_NAMES = ["arrived", "angle", "gx", "gy",
                    "qa", "qb", "qc", "qd", "x", "y", "z"]
