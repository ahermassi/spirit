from collections import namedtuple
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from .csv_analysis import analyze_data, load_surveys
from ..data.survey_utils import ExperimentType


TTEST_DIR = Path(__file__).parent.joinpath("../../models")

ColResult = namedtuple("ColResult", "col mu1 std1 mu2 std2 delta_mu t p g")


def hedges_g(sample1, sample2):
    n_samples = len(sample1) + len(sample2)
    return ((sample2.mean() - sample1.mean())
            / _std_weighted_pooled(sample1, sample2)
            * (n_samples - 3) / (n_samples - 2.25)
            * np.sqrt((n_samples - 2) / n_samples))


def _std_weighted_pooled(*samples):
    return np.sqrt(
        sum((len(sample) - 1) * sample.std()**2 for sample in samples)
        / (sum(len(sample) for sample in samples) - 2))


def do_ttest(df, columns, save_name=None,
             type1=ExperimentType.Onboard, type2=ExperimentType.Spirit):
    results = []

    for column in columns:
        sample1 = df[df.experiment_type == type1][column]
        sample2 = df[df.experiment_type == type2][column]
        ttest_result = stats.ttest_rel(sample2, sample1)

        results.append(
            ColResult(
                column,
                sample1.mean(), sample1.std(),
                sample2.mean(), sample2.std(),
                sample2.mean() - sample1.mean(),
                ttest_result.statistic, ttest_result.pvalue,
                hedges_g(sample1, sample2)
            )
        )

    if save_name is not None:
        df = pd.DataFrame(results).set_index("col")
        with open(TTEST_DIR.joinpath(f"ttest_{save_name}.tex"), "w") as fout:
            fout.write(df.to_latex())



if __name__ == "__main__":
    results, analyses = analyze_data()
    # analyses_columns = ["duration", "dist_err", "x_err", "y_err", "rms_x",
    #                     "rms_y", "path_length", "move_l", "move_r", "move_x",
    #                     "move_b", "move_f", "move_y"]
    # do_ttest(analyses, analyses_columns, "analyses")

    users, tlx, surveys = load_surveys()
    tlx_columns = ["mental", "physical", "temporal", "performance", "effort",
                   "frustration", "tlx"]
    survey_columns = ["orientation_understanding", "orientation_control",
                      "position_understanding", "position_control",
                      "spacial_understanding", "spacial_control", "total"]
    do_ttest(tlx, tlx_columns, save_name="tlx")
    do_ttest(surveys, survey_columns, save_name="survey")