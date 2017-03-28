# SPIRIT Data Collection

The source code for data collection is in the [Data](../src/data) directory.

* [`record_bag.py`](../src/data/record_bag.py) records the relevant data into a ROS Bag file. The output directory is [data/raw](data/raw) by default, but can be changed by modifying [`BAG_DIR`](../src/data/record_bag.py#L12). Similarly, [`ROSBAG_TOPICS`](../src/data/record_bag.py#L13) is the list of topics to record.

`record_bag.py` and `bag_to_csv.py` are to be used inside the docker container.
It may be possible to write a script which renames videos.
