import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

object_dict = {
    "Sun": {"Radius": 6.957e+8, "Orbital_Radius": 0, "Colour": "#FFFFFF"},
    "Earth": {"Radius": 6.378e+6, "Orbital_Radius": 1.496e+11, "Colour": "#64FFFF"},
    "Jupiter": {"Radius": 7.149e+7, "Orbital_Radius": 7.785e+11, "Colour": "#FFB4B4"},
    "Io": {"Radius": 1.822e+6, "Orbital_Radius": 4.217e+8, "Colour": "#808080"},
}

fine_simulations = []
for i in range(1, 21, 1):
    df = pd.read_csv("simulation_log/Fine Simulation {}.csv".format(i), index_col=0)
    fine_simulations.append({"df": df, "start_time": df.index[0], "end_time": df.index[df["Eclipse_observed"]][0]})
coarse_df = pd.read_csv("simulation_log/Coarse Simulation.csv", index_col=0)

def query_dataframe(simulation_time):
    '''given a simulation_time, we want to query the closest calculation to the given simulation_time'''
    row = None
    
    during_eclipse = False
    for fine in fine_simulations:
        if fine["start_time"] <= simulation_time and simulation_time <= fine["end_time"]:
            index = np.argmin(np.abs(fine["df"].index - simulation_time))
            during_eclipse = True
            row = fine["df"].iloc[index]
            break

    if not during_eclipse:
        index = np.argmin(np.abs(coarse_df.index - simulation_time))
        row = coarse_df.iloc[index]
    
    return row

CANVAS_SIZE = 2200
DISTANCE_SCALE = 5e+8
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

def plot_eclipse(X, Y, r, transform, scale, ax):
    pos = np.array([X, Y]).T
    render_pos = np.matmul(transform, pos)


    render = plt.Circle((render_pos[0, 0], render_pos[0, 1]), r / scale, facecolor="#FFFF6450", edgecolor="#FFFF6499", linewidth = 1)
    ax.add_patch(render)

SIMULATION_TIME = np.arange(0, 150000, 100)

for time in SIMULATION_TIME:
    row = query_dataframe(time)

    fig = plt.figure()
    ax = plt.axes(xlim=(-CANVAS_SIZE, CANVAS_SIZE), ylim=(-CANVAS_SIZE, CANVAS_SIZE))
    ax.set_facecolor("#000000")
    ax.set_aspect(1)

    Earth_X = row["Earth_X"]
    Earth_Y = row["Earth_Y"]
    Jupiter_X = row["Jupiter_X"]
    Jupiter_Y = row["Jupiter_Y"]

    if "Eclipse_Observation_Origin_X" in row:
        plot_eclipse(row["Eclipse_Observation_Origin_X"], row["Eclipse_Observation_Origin_Y"], row["Eclipse_Observation_Light_Front_Radius"], scale_down, DISTANCE_SCALE, ax)
        print("ECLIPSE")


    plot_orbits("Earth", DISTANCE_SCALE, ax)
    plot_orbits("Jupiter", DISTANCE_SCALE, ax)

    plot_object("Sun", 0, 0, scale_down, ax) # Sun 
    plot_object("Earth", Earth_X, Earth_Y, scale_down, ax) # Earth
    plot_object("Jupiter", Jupiter_X, Jupiter_Y, scale_down, ax) # Jupiter

    plt.savefig("render/{}.png".format(time))
    plt.close()