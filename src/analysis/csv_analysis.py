from collections import namedtuple
import glob
import pickle
from pathlib import Path
import re

import numpy as np
import pandas as pd

from ..data.survey_utils import ExperimentType


DATA_DIR = Path(__file__).parent.joinpath("../../data")
SURVEY_DIR = DATA_DIR.joinpath("raw")
CSV_DIR = DATA_DIR.joinpath("interim")


# Named Tuples
RunData = namedtuple("RunData", "experiment user run")
TlxResponse = namedtuple("TlxResponse", "code raw weight score")
Coords = namedtuple("Coords", "x y")
TARGET = Coords(0, 6)

# Regexes
FILENAME_PATTERN = "experiment-(\d)_user-(\d+)_run-(\d+)"
filename_regex = re.compile(pattern=FILENAME_PATTERN)


def distance(df, target):
    return np.sqrt((df.xn - target.x)**2 + (df.yn - target.y)**2)


def usable_filenames():
    filenames = sorted([filename for filename in glob.glob(f"{CSV_DIR}/*.csv")
                        if "user-99" not in filename])
    
    for filename in filenames:
        if filename_regex.search(filename):
            df = pd.read_csv(filename, parse_dates=["time"])
        else:
            continue
        if any(df.arrived):
            yield filename


def extract_run_data(filename):
    data = filename_regex.findall(filename)[0]
    return RunData(ExperimentType(int(data[0])), int(data[1]), int(data[2]))


def analyze_data():
    print("Loading files...")
    analyses = pd.DataFrame(columns="user experiment_type run "
                                    "dist_err x_err y_err "
                                    "dist_std x_std y_std "
                                    "rms rms_x rms_y "
                                    "idx_start idx_end t_start t_end duration "
                                    "path_length "
                                    "move_l move_r move_x "
                                    "move_b move_f move_y".split())
    
    records = []
    
    for i, filename in enumerate(usable_filenames()):
        df = pd.read_csv(filename, parse_dates=["time"])
        data = extract_run_data(filename)
        df.xn *= -1
        df.yn *= -1
        
        df["experiment_type"] = data.experiment
        df["user"] = data.user
        df["run"] = data.run
        records.append(df)
        
        found = df[df.arrived == 1]

        distances = distance(found, TARGET)
        dist_err = distances.mean()
        dist_std = distances.std()

        dx = found.xn - TARGET.x
        x_err = dx.mean()
        x_std = dx.std()

        dy = found.yn - TARGET.y
        y_err = dy.mean()
        y_std = dy.std()

        rms = np.sqrt(np.mean(((found.xn - TARGET.x)**2
                               + (found.yn - TARGET.y)**2)))
        rms_x = np.sqrt(np.mean((dx)**2))
        rms_y = np.sqrt(np.mean((dy)**2))
        
        t_start = df[df.z > 0.25].time.iloc[0]
        t_end = found.time.iloc[0]
        duration = (t_end - t_start).total_seconds()

        idx_start = df[df.time==t_start].index[0]
        idx_end = df[df.time==t_end].index[0]

        df_running = df[["xn", "yn"]].iloc[idx_start:idx_end+1]
        points = np.array(df_running)
        lengths = np.sqrt(np.sum(np.diff(points, axis=0)**2, axis=1))
        path = lengths.sum()

        diff_x = np.diff(points[:, 0])
        move_l = np.abs(np.sum(diff_x[diff_x > 0]))
        move_r = np.abs(np.sum(diff_x[diff_x < 0]))
        move_x = move_l + move_r

        diff_y = np.diff(points[:, 1])
        move_b = np.abs(np.sum(diff_y[diff_y > 0]))
        move_f = np.abs(np.sum(diff_y[diff_y < 0]))
        move_y = move_b + move_f

        analyses.loc[i] = [
            data.user, data.experiment, data.run,
            dist_err, x_err, y_err,
            dist_std, x_std, y_std,
            rms, rms_x, rms_y,
            idx_start, idx_end, t_start, t_end, duration,
            path,
            move_x, move_l, move_r,
            move_y, move_b, move_f,
        ]
        
    results = pd.concat(records, ignore_index=True)

    analyses["group"] = (analyses.user % 2).astype(int)
    analyses["start"] = [ExperimentType(e % 2 + 1) for e in analyses.user]
    analyses["experiment_int"] = [e.value for e in analyses.experiment_type]
    analyses["experiment"] = [e.name for e in analyses.experiment_type]
    analyses.experiment.replace("Spirit", "SPIRIT", inplace=True)

    results["group"] = (results.user % 2).astype(int)
    results["start"] = [ExperimentType(e % 2 + 1) for e in results.user]
    results["experiment_int"] = [e.value for e in results.experiment_type]
    results["experiment"] = [e.name for e in results.experiment_type]
    results.experiment.replace("Spirit", "SPIRIT", inplace=True)
    results.distance = distance(results, TARGET)
    results.dx = results.xn - TARGET.x
    results.dy = results.yn - TARGET.y
    results["total_ordering"] = (
        (results.run.diff(1) != 0)
        | (results.experiment_int.diff(1) != 0)
        | (results.user.diff(1) != 0)
    ).astype('int').cumsum() - 1

    for user in set(analyses.user):
        df = analyses[analyses.user == user].sort_values(
            by="experiment_int", ascending=np.all(analyses[analyses.user==user]
                                             .start==ExperimentType.Onboard))
        df["order"] = range(1, len(df) + 1)
        for idx in df.index:
            analyses.loc[idx, "order"] = int(df.loc[idx, "order"])
            results.loc[results.total_ordering==idx,
                        "order"] = int(df.loc[idx, "order"])

    for col in ["user", "run", "group", "order"]:
        analyses[col] = analyses[col].astype(int)
    for col in ["arrived", "order"]:
        results[col] = results[col].astype(int)

    print("Loaded files")
    return results, analyses


def load_surveys():
    print("Loading surveys...")
    with open(SURVEY_DIR.joinpath("survey_data.pkl"), "rb") as fin:
        data = pickle.load(fin)
    users = _load_users(data)
    tlx = _load_tlx(data)
    surveys = _load_surveys(data, tlx)
    print("Loaded surveys")
    return users, tlx, surveys


def _load_users(data):
    return pd.DataFrame({"user_id": user.id_, "name": user.name,
                         "age": user.age, "gender": user.gender,
                         "teleop": user.teleop, "flying": user.flying}
                        for user in data)


def _parse_tlx_component(component):
    return TlxResponse(component.code, component.score, component.weight,
                       component.weighted_score)


def _load_tlx(data):
    tlx_data = []
    for user in data:
        for experiment in user.experiments:
            d = {"user": user.id_, "experiment_type": experiment.type_}
            for component in experiment.tlx.components.values():
                parsed = _parse_tlx_component(component)
                d[parsed.code] = parsed.score
                d[f"{parsed.code}_raw"] = parsed.raw
            tlx_data.append(d)
    tlx = pd.DataFrame(tlx_data)
    tlx["group"] = tlx.user % 2
    tlx["tlx"] = (tlx.mental + tlx.physical + tlx.temporal
                  + tlx.performance + tlx.effort + tlx.frustration)
    tlx["order"] = [1, 2]*(len(tlx)//2)
    tlx["experiment_int"] = [e.value for e in tlx.experiment_type]
    tlx["experiment"] = [e.name for e in tlx.experiment_type]
    tlx.experiment.replace("Spirit", "SPIRIT", inplace=True)
    return tlx


def _load_surveys(data, tlx):
    survey_data = []

    for user in data:
        for experiment in user.experiments:
            d = {"user": user.id_, "experiment_type": experiment.type_}
            d.update({i.code:i.score
                      for i in experiment.survey.questions.values()})
            survey_data.append(d)

    surveys = pd.DataFrame(survey_data)
    surveys["group"] = tlx.user % 2
    surveys["order"] = [1, 2]*(len(surveys)//2)
    surveys["experiment"] = [e.name for e in surveys.experiment_type]
    surveys["experiment_int"] = [e.value for e in surveys.experiment_type]
    surveys["total"] = (surveys.orientation_understanding
                        + surveys.orientation_control
                        + surveys.position_understanding
                        + surveys.position_control
                        + surveys.spacial_understanding
                        + surveys.spacial_control)
    surveys.experiment.replace("Spirit", "SPIRIT", inplace=True)
    return surveys


if __name__ == "__main__":
    results, analyses = analyze_data()
    # analyze_differences(analyses, ["duration", "dist_err", "x_err", "y_err",
    #                                "rms_x", "rms_y"])
