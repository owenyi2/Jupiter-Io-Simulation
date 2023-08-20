import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Set up Basic Solar System

SUN_RADIUS = 6.957e+8
EARTH_RADIUS = 6.378e+6
JUPITER_RADIUS = 7.149e+7
IO_RADIUS = 1.822e+6

# Both Earth and Jupiter Move
EARTH_ORBITAL_PERIOD = 3.156e+7
JUPITER_ORBITAL_PERIOD = 3.784e+8
IO_ORBITAL_PERIOD = 1.530e+5

## Fix Jupiter in Place
# EARTH_ORBITAL_PERIOD = 1 / (1/3.156e+7 - 1/3.784e+8)
# JUPITER_ORBITAL_PERIOD = 1e+1000
# IO_ORBITAL_PERIOD = 1.530e+5

EARTH_ORBITAL_RADIUS = 1.496e+11
JUPITER_ORBITAL_RADIUS = 7.785e+11
IO_ORBITAL_RADIUS = 4.217e+8

class celestial_body:
    '''Generic class for celestial bodies Sun, Earth, Jupiter, Io'''

    def __init__(self, name, radius, orbital_radius, orbital_period, primary_body):
        self.name = name
        self.radius = radius
        self.orbital_radius = orbital_radius
        self.orbital_period = orbital_period

        self.primary_body = primary_body

        self.θ = None
        self.X = None
        self.Y = None

    def calculate_orbits(self, Time):
        if self.primary_body is None:
            self.θ = (2 * np.pi / self.orbital_period * Time) % (2*np.pi)
            self.X = self.orbital_radius * np.cos(self.θ)
            self.Y = self.orbital_radius * np.sin(self.θ)
        else:
            self.θ = (2 * np.pi / self.orbital_period * Time) % (2*np.pi)
            self.X = self.orbital_radius * np.cos(self.θ) + self.primary_body.X
            self.Y = self.orbital_radius * np.sin(self.θ) + self.primary_body.Y

def in_angle_interval(angle, angle1, angle2):
    '''Returns whether or not angle falls between the minor sector between angle1 and angle2 inclusive

    '''

    #Note: all angles in this calculation are assumed between [0, 2pi)

    larger_angle = np.maximum(angle1, angle2)
    smaller_angle = np.minimum(angle1, angle2)

    # Case 1: larger_angle - smaller_angle < np.pi: The minor sector spans from smaller_angle anticlockwise to larger_angle 
    # Case 2: larger_angle - smaller_angle > np.pi: The minor sector spans from larger_angle anticlockwise to smaller_angle
    # Case 3: larger_angle - smaller_angle = np.pi: Ambiguous case. Returns False.

    return np.logical_or(np.logical_and((larger_angle - smaller_angle) < np.pi,
                                        np.logical_and(angle >= smaller_angle, angle <= larger_angle)),
                         np.logical_and((larger_angle - smaller_angle) > np.pi,
                                        np.logical_or(angle < smaller_angle, angle > larger_angle))
                                        )
                         

# Step 2: Coarse Simulation

coarse_resolution = 120
TIME_INDEX = np.arange(0, 3.46e+7, coarse_resolution)

Sun = celestial_body("Sun", SUN_RADIUS, 0, 1, None)
Earth = celestial_body("Earth", EARTH_RADIUS, EARTH_ORBITAL_RADIUS, EARTH_ORBITAL_PERIOD, Sun)
Jupiter = celestial_body("Jupiter", JUPITER_RADIUS, JUPITER_ORBITAL_RADIUS, JUPITER_ORBITAL_PERIOD, Sun)
Io = celestial_body("Io", IO_RADIUS, IO_ORBITAL_RADIUS, IO_ORBITAL_PERIOD, Jupiter)
Observatory = celestial_body("Observatory", 0, EARTH_RADIUS, 86400, Earth)

Sun.calculate_orbits(TIME_INDEX)
Earth.calculate_orbits(TIME_INDEX)
Jupiter.calculate_orbits(TIME_INDEX)
Io.calculate_orbits(TIME_INDEX)
Observatory.calculate_orbits(TIME_INDEX)

# Step 3: Compute Eclipses of Io

def calculate_io_eclipses(Jupiter, Io):
    '''Compute when Io is behind Jupiter's Shadow
    
    To do this, we calculate the critical angles that the edges of Jupiter's shadow makes on the circle of Io's orbit

    eclipse_α is the angle adjacent to Jupiter's radius in the triangle made by an edge of Jupiter's Shadow, Jupiter's radius tangent to the Shadow edge and the radius of Io's orbit that meets Jupiter's shadow
    Refering to Eclpise Calculation.png, eclipse_angle_1 is the angle to the positive horizontal of AF 
    '''
    eclipse_α = np.arccos(Jupiter.radius / Io.orbital_radius)
    eclipse_angle_1 = (-np.pi/2 + Jupiter.θ + eclipse_α) % (2 * np.pi)
    eclipse_angle_2 = (np.pi/2 + Jupiter.θ - eclipse_α) % (2 * np.pi)

    '''Note: We are making a simplification to the code by determining if Io is eclipsed by Jupiter based on the centre point of Io. In observation, we would define emergence and immersion based on the position of the perimeter of Io relative to the shadow.'''
    Io_eclipsed = in_angle_interval(Io.θ, eclipse_angle_1, eclipse_angle_2)

    Io_eclipsed_shifted = np.roll(Io_eclipsed, 1) # We shift it forward one index
    Io_eclipsed_shifted[0] = np.nan

    return np.logical_and(np.logical_not(np.equal(Io_eclipsed, Io_eclipsed_shifted)), Io_eclipsed) #signal at emergence

Eclipse = calculate_io_eclipses(Jupiter, Io)

coarse_df = pd.DataFrame(data={
    "Earth_θ": Earth.θ,
    "Earth_X": Earth.X,
    "Earth_Y": Earth.Y,
    "Observatory_θ": Observatory.θ,
    "Observatory_X": Observatory.X,
    "Observatory_Y": Observatory.Y,
    "Jupiter_θ": Jupiter.θ,
    "Jupiter_X": Jupiter.X,
    "Jupiter_Y": Jupiter.Y,
    "Io_θ": Io.θ,
    "Io_X": Io.X,
    "Io_Y": Io.Y,
    "Eclipse": Eclipse
}, index=TIME_INDEX)

print(coarse_df.index)
input()
coarse_df.to_csv("simulation_log/Coarse Simulation.csv")

eclipse_times = coarse_df.loc[coarse_df['Eclipse']].index.values

# Step 4: Fine Simulation

class Light:
    def __init__(self, X, Y, start, r=0, c = 299792458):
        self.X = X
        self.Y = Y
        self.r = r
        self.c = c
        self.start = start

    def propagate(self, Time):
        self.r = np.maximum(self.c * (Time - self.start), np.zeros_like(Time))

    def check_received(self, observatory):
        # observatory is an object with a attributes for position (observatory.X, observatory.Y)

        self.received = np.linalg.norm(np.stack([observatory.X - self.X, observatory.Y - self.Y]), axis=0) < self.r
        return self.received
    
def plot_solar_system_at_time_step(solar_system, index, plot_limit):
    fig = plt.figure()
    ax = plt.axes(xlim=(-plot_limit, plot_limit), ylim=(-plot_limit, plot_limit))
    ax.axis('equal')

    for celestial_body in solar_system:
        render = plt.Circle((celestial_body.X[index], celestial_body.Y[index]), 1e+10)
        ax.add_patch(render)

    plt.show()

fine_resolution = 0.1
previous_eclipse_observed_time = 0
current_eclipse_observed_time = 0
io_observed_periods = []
fine_dfs = []

for eclipse_time in eclipse_times:
    FINE_TIME_INDEX =  np.arange(eclipse_time - coarse_resolution, eclipse_time+3500, fine_resolution)

    # recalculate eclipse time more precisely
    Sun.calculate_orbits(FINE_TIME_INDEX)
    Earth.calculate_orbits(FINE_TIME_INDEX)
    Jupiter.calculate_orbits(FINE_TIME_INDEX)
    Io.calculate_orbits(FINE_TIME_INDEX)
    Observatory.calculate_orbits(FINE_TIME_INDEX)

    Eclipse = calculate_io_eclipses(Jupiter, Io)
    exact_eclipse_index = np.nonzero(Eclipse)[0][0]

    eclipse_observation = Light(Io.X[exact_eclipse_index], Io.Y[exact_eclipse_index], FINE_TIME_INDEX[exact_eclipse_index])
    eclipse_observation.propagate(FINE_TIME_INDEX)
    eclipse_observed = eclipse_observation.check_received(Observatory) # We are taking the centre of the Earth as the observatory meaning an observation is recorded when light would pass the centre of the Earth

    eclipse_observed_index = np.nonzero(eclipse_observed)[0][0] # Grab the index of the first True value
    eclipse_observed_time = FINE_TIME_INDEX[eclipse_observed_index] # Convert said index to a time

    fine_df = pd.DataFrame(data={
        "Earth_θ": Earth.θ,
        "Earth_X": Earth.X,
        "Earth_Y": Earth.Y,
        "Observatory_θ": Observatory.θ,
        "Observatory_X": Observatory.X,
        "Observatory_Y": Observatory.Y,
        "Jupiter_θ": Jupiter.θ,
        "Jupiter_X": Jupiter.X,
        "Jupiter_Y": Jupiter.Y,
        "Io_θ": Io.θ,
        "Io_X": Io.X,
        "Io_Y": Io.Y,
        "Eclipse": Eclipse,
        "Eclipse_Observation_Origin_X": eclipse_observation.X,
        "Eclipse_Observation_Origin_Y": eclipse_observation.Y,
        "Eclipse_Observation_Light_Front_Radius": eclipse_observation.r,
        "Eclipse_observed": eclipse_observed,
    }, index=FINE_TIME_INDEX)

    # print(fine_df.index)
    fine_dfs.append(fine_df)
    # fine_df.to_csv("simulation_log/Fine Simulation start {}.csv".format(eclipse_time - coarse_resolution))

    previous_eclipse_observed_time = current_eclipse_observed_time
    current_eclipse_observed_time = eclipse_observed_time

    # plot_solar_system_at_time_step([Sun, Earth, Jupiter, Io], eclipse_observed_index, 1e+12)

    io_observed_periods.append((current_eclipse_observed_time - previous_eclipse_observed_time))
io_observed_periods = np.array(io_observed_periods[1:]) 

# Step 5: Output main results
with open("data.txt", "w") as f:
    f.write(str(list(io_observed_periods)))
plt.plot(io_observed_periods / 3600)
plt.title("Time Deviation (s)")
plt.xlabel("Eclipse Number")
plt.ylabel("Period (hr)")
plt.grid()
plt.savefig("Io Periods.png")

print("Maximum Accumlated Time Difference (min): {}".format(1/60 * np.sum(io_observed_periods[io_observed_periods>np.mean(io_observed_periods)] - np.mean(io_observed_periods))))
print("Difference in Time between Longest Apparent Period and Shortest Apparent Period (s): {}".format(max(io_observed_periods)-min(io_observed_periods)))

# Step 6: Downsample raw data for rendering

# coarse_df["Eclipse_Observation_Origin_X"] = None
# coarse_df["Eclipse_Observation_Origin_Y"] = None
# coarse_df["Eclipse_Observation_Light_Front_Radius"] = None
# coarse_df["Eclipse_observed"] = None
# concat_list = []

# for i in range(226):
#     fine_df = fine_dfs[i]
    
#     downsample_rate = round(coarse_resolution / fine_resolution)
    
#     eclipse_start_fine_integer_index = fine_df.index.get_loc(fine_df.index[fine_df["Eclipse"]][0])
#     eclipse_start_coarse_integer_index = coarse_df.index.get_loc(coarse_df.index[coarse_df["Eclipse"]][i])

#     eclipse_end_fine_integer_index = fine_df.index.get_loc(fine_df.index[fine_df["Eclipse_observed"]][0]) + downsample_rate
#     eclipse_end_coarse_integer_index = np.argmin(np.abs(coarse_df.index - fine_df.index[fine_df["Eclipse_observed"]][0]))

#     fine_df_downsample = fine_df.iloc[eclipse_start_fine_integer_index:eclipse_end_fine_integer_index:downsample_rate]

#     print(eclipse_start_fine_integer_index)
#     print(eclipse_start_coarse_integer_index)
#     print(eclipse_end_fine_integer_index)
#     print(eclipse_end_coarse_integer_index)

#     coarse_df.loc[coarse_df.index[eclipse_start_coarse_integer_index]:coarse_df.index[eclipse_end_coarse_integer_index], ["Earth_θ"]] = "DELETE ME"

#     concat_list.append(fine_df_downsample)    
    

# coarse_df = coarse_df[coarse_df["Earth_θ"] != "DELETE ME"]
# concat_list.append(coarse_df)

# # coarse_df.to_csv("simulation_log/Coarse Simulation.csv")
# down_sample_df = pd.concat(concat_list)
# down_sample_df = down_sample_df.sort_index()
# down_sample_df.to_csv("simulation_log/down_sample.csv")