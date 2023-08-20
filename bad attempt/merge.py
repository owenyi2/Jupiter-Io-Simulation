import pandas as pd
import numpy as np

eclipse = 1
coarse_df = pd.read_csv("simulation_log/Coarse Simulation.csv", index_col=0)
coarse_resolution = 100
fine_resolution = 0.1

new_df = coarse_df.copy()
new_df["Eclipse_Observation_Origin_X"] = None
new_df["Eclipse_Observation_Origin_Y"] = None
new_df["Eclipse_Observation_Light_Front_Radius"] = None
new_df["Eclipse_observed"] = None


for eclipse in range(1, 21, 1):
    fine_df = pd.read_csv("simulation_log/Fine Simulation {}.csv".format(eclipse), index_col=0)
    fine_index = fine_df.index
    start_time = fine_index[0]
    end_time = fine_index[-1]

    coarse_index = coarse_df.index
    start_integer_index = np.argmin(np.abs(coarse_index - start_time))
    end_integer_index = np.argmin(np.abs(coarse_index - end_time)) - 1

    new_df.drop(new_df.index[start_integer_index:end_integer_index], inplace=True)
    new_df = pd.concat([new_df, fine_df], axis = 0)

new_df.sort_index(inplace=True)

print(len(new_df))
new_df.to_csv("simulation_log/merged simulation.csv")
