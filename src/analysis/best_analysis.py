from collections import namedtuple
from pathlib import Path
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymc3 as pm

from .csv_analysis import analyze_data, load_surveys
from ..data.survey_utils import ExperimentType
from ..visualization.latexify import latexify, figure


BEST_DIR = Path(__file__).parent.joinpath("../../models")
BestResult = namedtuple("BestResult", "trace model")


def best(sample1, sample2, σ_range, exponential_m, n_iter=2000, n_jobs=2):
    y1 = np.array(sample1)
    y2 = np.array(sample2)
    y = pd.DataFrame(dict(value=np.r_[y1, y2],
                          group=np.r_[["onboard"] * len(sample1),
                                      ["spirit"] * len(sample2)]))
    μ_m = y.value.mean()
    μ_s = y.value.std() * 2

    with pm.Model() as model:
        group1_mean = pm.Normal("group1_mean", μ_m, sd=μ_s)
        group2_mean = pm.Normal("group2_mean", μ_m, sd=μ_s)
        σ_low, σ_high = σ_range
        group1_std = pm.Uniform("group1_std", lower=σ_low, upper=σ_high)
        group2_std = pm.Uniform("group2_std", lower=σ_low, upper=σ_high)
        ν = pm.Exponential("ν_minus_one", abs(1 / (exponential_m - 1))) + 1

        λ1 = group1_std ** -2
        λ2 = group2_std ** -2

        group1 = pm.StudentT("onboard",
                             nu=ν, mu=group1_mean, lam=λ1, observed=y1)
        group2 = pm.StudentT("spirit",
                             nu=ν, mu=group2_mean, lam=λ2, observed=y2)

        diff_of_means = pm.Deterministic("difference of means",
                                         group1_mean - group2_mean)
        diff_of_stds = pm.Deterministic("difference of stds",
                                        group1_std - group2_std)
        effect_size = pm.Deterministic("effect size",
                                       diff_of_means / np.sqrt(
                                           (group1_std ** 2 + group2_std ** 2)
                                           / 2))
        trace = pm.sample(n_iter, init=None, njobs=n_jobs)
    return BestResult(trace, model)


def summarize(best_result, kde=True, plot=True, column=None):
    trace, model = best_result
    if plot:
        ax = pm.plot_posterior(trace[100:],
                               varnames=[r"group1_mean", r"group2_mean",
                                         r"group1_std", "group2_std",
                                         r"ν_minus_one"],
                               kde_plot=kde, color="C0")
        if kde:
            for a in (1, 3):
                ax[a].lines[0].set_color("C1")
        plt.figure()
        pm.plot_posterior(trace[1000:],
                          varnames=["difference of means", "difference of stds",
                                    "effect size"],
                          ref_val=0, kde_plot=True, color="C2")
        plt.figure()
        pm.forestplot(trace[1000:], varnames=[v.name for v in model.vars[:2]])
        plt.figure()
        pm.forestplot(trace[1000:], varnames=[v.name for v in model.vars[2:]])

    pm.summary(trace[1000:],
               varnames=["difference of means", "difference of stds",
                         "effect size"])

    if column is not None:
        pm.summary(trace[1000:],
                   varnames=["difference of means", "difference of stds",
                             "effect size"],
                   to_file=BEST_DIR.joinpath(f"best_{column}_pretty.txt"))
        df = pm.df_summary(trace[1000:],
                           varnames=["difference of means",
                                     "difference of stds", "effect size"])
        with open(BEST_DIR.joinpath(f"best_{column}_df.txt"), "w") as fout:
            fout.write(str(df))


def analyze_differences(df, columns, params, n_iter=2000, n_jobs=2,
                        show_summaries=True, plot=False, save=True):
    traces = {}
    for column, param in zip(columns, params):
        print(f"Analyzing difference in {column}...")
        sample1 = df[df.experiment_type == ExperimentType.Onboard][column]
        sample2 = df[df.experiment_type == ExperimentType.Spirit][column]
        best_result = best(sample1, sample2, *param,
                           n_iter=n_iter, n_jobs=n_jobs)
        traces[column] = best_result
        if show_summaries:
            summarize(best_result, plot=plot, column=column)
        if save:
            with open(BEST_DIR.joinpath(f"best_{column}.pkl"), "wb") as fout:
                pickle.dump(best_result, fout)
    return traces


def load_best_result(column):
    with open(BEST_DIR.joinpath(f"best_{column}.pkl"), "rb") as fin:
        return pickle.load(fin)


def _do_differences(df, trace_cols, trace_coeffs, recalculate=False):
    if recalculate:
        traces = analyze_differences(df, trace_cols, trace_coeffs)
    else:
        traces = {col: load_best_result(col) for col in trace_cols}
    for col, best_result in traces.items():
        trace = best_result.trace
        with figure(f"mean_std_{col}"):
            ax = pm.plot_posterior(trace[100:],
                                   varnames=[r"group1_mean", r"group2_mean",
                                             r"group1_std", r"group2_std"],
                                   kde_plot=True, color="C0")
            for a in (1, 3):
                ax[a].lines[0].set_color("C1")

        with figure(f"difference_{col}"):
            # noinspection PyTypeChecker
            pm.plot_posterior(trace[1000:],
                              varnames=["difference of means", "effect size"],
                              ref_val=0, kde_plot=True, color="C2")


def do_differences_analyses(recalculate=False):
    trace_cols = ["duration", "dist_err", "x_err", "y_err", "rms_x", "rms_y",
                  "path_length", "move_l", "move_r", "move_x", "move_b",
                  "move_f", "move_y"]
    trace_coeffs = ([[(5, 50), 50]] + [[(0, 2), 0.5]]*5
                    + [[(0, 10), 10], [(0, 5), 3], [(0, 5), 3], [(0, 10), 6],
                       [(0, 5), 1.5], [(0, 5), 7], [(0, 10), 9]])

    _do_differences(analyses, trace_cols, trace_coeffs, recalculate)


def do_differences_surveys(recalculate=False):
    trace_cols = ["orientation_understanding", "orientation_control",
                  "position_understanding", "position_control",
                  "spacial_understanding", "spacial_control", "total"]
    trace_coeffs = [[(0, 7), 2]]*6 + [[(0, 42), 10]]

    _do_differences(surveys, trace_cols, trace_coeffs, recalculate)


def do_differences_tlx(recalculate=False):
    trace_cols = [
        "mental",
        # "physical",  # Physical does not converge.
        "temporal",
        "performance",
        "effort",
        "frustration",
        "tlx",
    ]
    trace_coeffs = [[(0, 45), 20]]*(len(trace_cols) - 1) + [[(0, 250), 100]]

    _do_differences(tlx, trace_cols, trace_coeffs, recalculate)


if __name__ == "__main__":
    latexify()

    # WARNING: Takes a long time with recalculate.
    results, analyses = analyze_data()
    do_differences_analyses(recalculate=True)

    users, tlx, surveys = load_surveys()
    # do_differences_surveys(recalculate=True)
    # do_differences_tlx(recalculate=True)