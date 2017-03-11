from contextlib import contextmanager
from pathlib import Path
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


INCHES_PER_PT = 1/72.27  # Convert pt to inch
MAX_HEIGHT_INCHES = 8


def latexify():
    """
    Set up matplotlib's RC params for LaTeX plotting.

    Call this before plotting a figure.

    """
    params = {
        "pgf.texsystem": "xelatex",  # change this if using xetex or lautex
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": [],
        "font.sans-serif": [],
        "font.monospace": [],
        "pgf.preamble": [
          r"\usepackage[utf8x]{inputenc}",
          r"\usepackage[T1]{fontenc}",
          ],
        "font.size": 8,
        "axes.labelsize": 8,  # fontsize for x and y labels (was 10)
        "axes.titlesize": 8,
        "legend.fontsize": 8,  # was 10
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
    }

    mpl.rcParams.update(params)
    plt.switch_backend("pgf")


def fig_size(fig_width_tw=None, fig_ratio=None, fig_height=None, n_columns=1,
             doc_width_pt=345):
    r"""
    Get the necessary figure size.

    Parameters
    ----------
    fig_width_tw : Optional[float]
        The width of the figure, as a proportion of the text width. Should be
        between 0 and 1. Default is 0.9.
    fig_ratio: Optional[float]
        The ratio of the figure height to figure width. Default is the golden
        ratio.
    fig_height : Optional[float]
        The height of the figure in inches. Default is the golden ratio with
        the figure width.
    n_columns : Optional[int]
        The number of columns in the document. Default is 1.
    doc_width_pt : float
        The text width of the document, in points. Can be obtained by typing
        `\the\textwidth` in the LaTeX document. Default is 345.

    Returns
    -------
    fig_width : float
        The figure width, in inches.
    fig_height : float
        The figure height in inches.

    """
    fig_width_in = doc_width_pt * INCHES_PER_PT

    if fig_width_tw is None:
        fig_width = fig_width_in * 0.9 / n_columns
    else:
        fig_width = fig_width_in * fig_width_tw

    if fig_ratio is None:
        if fig_height is None:
            golden_mean = (np.sqrt(5)-1.0)/2.0    # Aesthetic ratio
            fig_ratio = golden_mean
        else:
            fig_ratio = fig_height / fig_width

    fig_height = fig_width * fig_ratio # height in inches

    if fig_height > MAX_HEIGHT_INCHES:
        print(f"WARNING: fig_height too large at {fig_height} inches, so will "
              "reduce to {MAX_HEIGHT_INCHES} inches.",
              file=sys.stderr
              )
        fig_height = MAX_HEIGHT_INCHES
    return fig_width, fig_height


def save_fig(filename, folder="img", from_context=False, exts=("pgf", "pdf")):
    if not from_context:
        print(f"Saving {filename}...  ")
    plt.tight_layout(0)
    for ext in exts:
        if from_context:
            print(f"  Saving {ext}...")
        plt.savefig(str(Path(folder).joinpath(f"{filename}.{ext}")))


@contextmanager
def figure(filename, folder="../img/plots", size=fig_size(),
           exts=("pgf", "pdf")):
    print(f"{filename}:")
    print("  Plotting...")
    yield
    plt.gcf().set_size_inches(*size)
    save_fig(filename, folder=folder, from_context=True, exts=exts)
    plt.close()


if __name__ == "__main__":
    latexify()
    x = np.linspace(-np.pi, np.pi)
    y = np.sin(x)
    y2 = np.cos(x)
    with figure("latexify"):
        plt.plot(x, y, label=r"$\sin(\theta)$")
        plt.plot(x, y2, label=r'$\cos(\theta)$')
        plt.legend()
        plt.xlabel(r"$\theta$")
        plt.ylabel("Magnitude")
