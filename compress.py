import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

fine_simulations = []
for i in range(1, 21, 1):
    df = pd.read_csv("simulation_log/Fine Simulation {}.csv".format(i), index_col=0)
    fine_simulations.append({"df": df, "start_time": df.index[0], "end_time": df.index[df["Eclipse_observed"]][0] + 100})
coarse_df = pd.read_csv("simulation_log/Coarse Simulation.csv", index_col=0)

coarse_df["Eclipse_Observation_Origin_X"] = None
coarse_df["Eclipse_Observation_Origin_Y"] = None
coarse_df["Eclipse_Observation_Light_Front_Radius"] = None
coarse_df["Eclipse_observed"] = None

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

SIMULATION_TIME = np.arange(0, 3160000, 100)
row_list = []

for time in SIMULATION_TIME:
    row = query_dataframe(time)
    row_list.append(row)

df = pd.DataFrame(row_list)
df = df.iloc[:19900]
df.to_csv("simulation_log/downsampled simulation 2.csv")
