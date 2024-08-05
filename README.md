# 3D-heat-transport

if one needs to simulate solid material heating (temperature distribution), then one can use this code.

while 4d plotting you should be able to distinguish copper radiator and surrounding water after at least 2 seconds of simulated time

the aim is to determine TDPs of different fin geometries

to achieve this aim:

# heat transport inside copper/any_material radiator will be computed

# decrease of temperature of radiator surface will be performed

currently at stage no. 2. note, that one full iteration of loops takes 2-6 (code dependendent) min on my i3 4000m. night is long. and this 2 min is just 0.05 s. i cannot use colab, neither pc

another code measures max heat transfer at the interface - relative to energy added
