import pandas as pd
import numpy as np

df = pd.read_csv("simulation_log/merged simulation.csv", index_col=0)
resolution = 60 # seconds of simulation time per frame
fps = 60

print("run_time (minutes): {}".format(round(df.index[-1]/resolution) / fps / 60))

sim_index = np.arange(0, df.index[-1], resolution)
print(sim_index)

def f(x):
    return np.argmin(np.abs(df.index - x))
    
out = np.array([f(xi) for xi in sim_index])

df.iloc[out].to_csv("simulation_log/downsampled simulation.csv")
    # time = resolution * i
    # index = np.argmin(np.abs(df.index - time))

# index = [np.argmin(np.abs(df.index - resolution * i)) for i in range(round(df.index[-1]/resolution))]