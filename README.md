# 3D-heat-transport

note: all of the voxels have dimensions of 1x1x1 meter. 

meter. 

simulation time is proportional to simulated volume. if one simulate bigger volume, then: 

# time = (desired_volume/simulated_volume)*simulation_time

if one needs to simulate solid material heating (temperature distribution), then one can use this code.

the aim is to determine TDPs of different fin geometries

another code measures max heat transfer at the interface - relative to energy added, to obtain transfered_heat vs time curve

# python integrators are unstable. c++ is the solution
