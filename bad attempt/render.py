import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

CANVAS_SIZE = 2200
DISTANCE_SCALE = 5e+8

object_dict = {
    "Earth": {"Radius": 6.378e+6, "Orbital_Radius": 1.496e+11, "Colour": "#64FFFF"},
    "Sun": {"Radius": 6.957e+8, "Orbital_Radius": 0, "Colour": "#FFFFFF"},
    "Jupiter": {"Radius": 7.149e+7, "Orbital_Radius": 7.785e+11, "Colour": "#FFB4B4"},
}

df = pd.read_csv("simulation_log/Coarse Simulation.csv", index_col=0)

scale_down = np.matrix([[1 / DISTANCE_SCALE, 0], [0, 1 / DISTANCE_SCALE]])

def plot_object(name, X, Y, transform, ax):
    r = np.sqrt(object_dict[name]["Radius"] / DISTANCE_SCALE * 10000)
    pos = np.array([X, Y]).T
    render_pos = np.matmul(transform, pos)
    render = plt.Circle((render_pos[0, 0], render_pos[0, 1]), r, color = object_dict[name]["Colour"])
    ax.add_patch(render)


def plot_orbits(name, scale, ax):
    render = plt.Circle((0, 0), object_dict[name]["Orbital_Radius"] / scale, facecolor = "#00000000", edgecolor = "#FFFFFF99", linewidth = 1)
    ax.add_patch(render)

eclipse_occuring = True

for frame in range(0, len(df)):
    fig = plt.figure()
    ax = plt.axes(xlim=(-CANVAS_SIZE, CANVAS_SIZE), ylim=(-CANVAS_SIZE, CANVAS_SIZE))
    ax.set_facecolor("#000000")
    ax.set_aspect(1)

    row = df.iloc[frame]
    Earth_X = row["Earth_X"]
    Earth_Y = row["Earth_Y"]
    Jupiter_X = row["Jupiter_X"]
    Jupiter_Y = row["Jupiter_Y"]

    plot_orbits("Earth", DISTANCE_SCALE, ax)
    plot_orbits("Jupiter", DISTANCE_SCALE, ax)

    plot_object("Sun", 0, 0, scale_down, ax) # Sun 
    plot_object("Earth", Earth_X, Earth_Y, scale_down, ax) # Earth
    plot_object("Jupiter", Jupiter_X, Jupiter_Y, scale_down, ax) # Jupiter

