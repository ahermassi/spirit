from collections import namedtuple

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import seaborn.apionly as sns


Coords = namedtuple("Coords", "x y")
TARGET = Coords(0, 6)


def change_color(color, saturation=0, value=0):
    rgb = mpl.colors.ColorConverter.to_rgb(color)
    h, s, v = mpl.colors.rgb_to_hsv(rgb)
    s *= 1 + saturation / 100
    s = np.clip(s, 0, 1)
    v *= 1 + value / 100
    v = np.clip(v, 0, 1)
    r, g, b = mpl.colors.hsv_to_rgb((h, s, v))
    return r, g, b


def plot_overview(df, experiment_type, color="C0", title=None, target=TARGET,
                  alpha_path=0.2, width_path=0.5, zorder_path=0,
                  alpha_point=1, size_point=1, zorder_point=1, crosshair=False,
                  drone_width=None, xlabel="$x$ (m)", ylabel="$y$ (m)"):
    df_ex = df[df.experiment_type == experiment_type]
    df_arr = df_ex[df_ex.arrived == 1]
    if title is None:
        title = df_ex.experiment.iloc[0]
    for run in set(df_ex.total_ordering):
        df_run = df_ex[df_ex.total_ordering == run]
        plt.plot(df_run.xn, df_run.yn, alpha=alpha_path, color=color,
                 zorder=zorder_path, lw=width_path)
    plt.scatter(df_arr.xn, df_arr.yn, alpha=alpha_point, color=color,
                zorder=zorder_point, s=size_point)
    plot_targets(show_start=True, show_final=False, target_coords=[target],
                 drone_width=drone_width, crosshair=crosshair)
    plt.axis("equal")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)


def plot_by_distance(df, experiment_type, cmap="C0", target=TARGET,
                     alpha_point=0.5, zorder_point=1, crosshair=False,
                     xlabel="$x$ (m)", ylabel="$y$ (m)"):
    df_ex = df[df.experiment_type == experiment_type]
    df_arr = df_ex[df_ex.arrived == 1]
    plt.scatter(df_arr.xn, df_arr.yn, alpha=alpha_point, zorder=zorder_point,
                c=df_arr.distance, cmap=cmap)
    plt.colorbar(label="distance (m)")
    plt.clim(df[df.arrived == 1].distance.min(),
             df[df.arrived == 1].distance.max())
    plot_targets(show_start=False, show_final=False, target_coords=[target],
                 crosshair=crosshair)
    plt.axis("equal")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)


def plot_detailed(df, experiment_type, color="C0", title=None, target=TARGET,
                  alpha_point=1, size_point=1, zorder_point=1, crosshair=False,
                  drone_width=None, xlabel="$x$ (m)", ylabel="$y$ (m)"):
    df_ex = df[df.experiment_type == experiment_type]
    df_arr = df_ex[df_ex.arrived == 1]
    if title is None:
        title = df_ex.experiment.iloc[0]
    for order in np.arange(1, df.order.max() + 1):
        df_run = df_arr[df_arr.order == order]
        plt.scatter(df_run.xn, df_run.yn,
                    label=f"Run {order}", s=size_point, alpha=alpha_point,
                    color=change_color(color, value=-50 + 25 * (order - 1)),
                    zorder=zorder_point)
    plot_targets(show_start=False, show_final=False, target_coords=[target],
                 crosshair=crosshair, drone_width=drone_width)
    plt.title(title)
    plt.axis("equal")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()


def plot_distribution(df, experiment_type, color="C0", title=None,
                      target_color="C2", background_shade=-50,
                      crosshair=False, drone_width=None):
    df_ex = df[df.experiment_type == experiment_type]
    df_arr = df_ex[df_ex.arrived == 1]
    if title is None:
        title = df_ex.experiment.iloc[0]
    g = sns.jointplot(df_arr.xn, df_arr.yn, kind="kde", space=0, color=color)
    g.plot_marginals(sns.rugplot, height=0.1, color=color)
    g.ax_joint.get_children()[0].set_zorder(-1)
    for child in g.ax_joint.get_children()[1:]:
        if isinstance(child, mpl.collections.PathCollection):
            child.set_alpha(0.8)
    plt.sca(g.ax_joint)
    plot_targets(show_start=False, show_final=False, target_coords=[TARGET],
                 target_color=target_color, zorder=0, crosshair=crosshair,
                 drone_width=drone_width)
    g.set_axis_labels("$x$", "$y$")
    plt.axis("equal")

    xmin, xmax = plt.xlim()
    ymin, ymax = plt.ylim()
    xsize = xmax - xmin
    ysize = ymax - ymin

    if xsize > ysize:
        ymin -= (xsize - ysize) / 2
        ymax += (xsize - ysize) / 2
        ysize = xsize
    else:
        xmin -= (ysize - xsize) / 2
        xmax += (ysize - xsize) / 2
        xsize = ysize

    plt.gca().add_patch(mpl.patches.Rectangle(
        (min(xmin, ymin) - abs(min(xmin, ymin)),
         min(xmin, ymin) - abs(min(xmin, ymin))),
        max(xsize, ysize) * 5, max(xsize, ysize) * 5,
        color=change_color(color, saturation=background_shade),
        zorder=-1))
    g.fig.suptitle(title)


def plot_targets(p_init=Coords(0, 0), p_final=Coords(0, 0),
                 invert_x=False, invert_y=False,
                 target_coords=None, target_coord_offsets=None,
                 target_color="C2", target_size=Coords(0.525, 0.37),
                 show_start=True, show_final=True,
                 scale=100, zorder=0, crosshair=False, drone_width=None,
                 background_shade=-50):
    if target_coords is not None and target_coord_offsets is not None:
        raise ValueError("Use either target_coords or target_coord_offsets")

    ax = plt.gca()

    if target_coords is None:
        target_coords = [Coords(p_init.x - offset.x, p_init.y - offset.y)
                         for offset in target_coord_offsets]

    if show_start:
        plt.scatter(-p_init.x, -p_init.y, marker=(5, 0), s=100, c="g")

    for coord in target_coords:
        if crosshair:
            plt.axhline(coord.y,
                        color=change_color(target_color,
                                           value=background_shade / 2),
                        zorder=zorder, lw=0.5)
            plt.axvline(coord.x,
                        color=change_color(target_color,
                                           value=background_shade / 2),
                        zorder=zorder, lw=0.5)
        if drone_width is not None:
            ax.add_patch(mpl.patches.Rectangle(
                (coord.x * (-1 if invert_x else 1)
                 - target_size.x / 2 - drone_width / 2,
                 coord.y * (-1 if invert_y else 1)
                 - target_size.y / 2 - drone_width / 2),
                target_size.x + drone_width,
                target_size.y + drone_width,
                fill=False, lw=0.5, linestyle="dotted",
                edgecolor=change_color(target_color,
                                       value=background_shade / 2),
                zorder=zorder))

        ax.add_patch(mpl.patches.Rectangle(
            (coord.x * (-1 if invert_x else 1) - target_size.x / 2,
             coord.y * (-1 if invert_y else 1) - target_size.y / 2),
            target_size.x,
            target_size.y,
            color=target_color,
            zorder=zorder))

    if show_final:
        plt.scatter(p_final.x * (-1 if invert_x else 1),
                    p_final.y * (-1 if invert_y else 1),
                    marker=(3, 0), s=scale, c="r")