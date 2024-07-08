import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
from tqdm import tqdm
# Load temperature data     /home/tomkow1029/Desktop/temp_solver/temp_geo_plotter.py
try:
    temp = np.load("temp_0.npy")
except FileNotFoundError as e:
    print("\n\n\n\ncheck your path, you idiot...\n\n\n\n")

alpha = 0.3
mini = 292 # kelvins
maxi = np.max(temp)

ct = np.empty((len(temp), len(temp[0]), len(temp[0,0]), 4), dtype=np.float16) # voxels and rgba
for x in tqdm(range(len(temp))):
    for y in range(len(temp[0])):
        for z in range(len(temp[0,0])):
            if temp[x,y,z]>100:
                ct[x, y, z, 0] = (temp[x, y, z] - mini)  / (maxi - mini)  # RGB channels - red-blue lut
                ct[x,y,z,1]=0.0
                ct[x,y,z,2]=1.0-(temp[x, y, z] - mini) / (maxi - mini)
                ct[x, y, z, 3] = alpha  # Alpha channel
            else:
                ct[x,y,z,:]=0.0 # if empty, then fill!

fig = plt.figure()
n = 3 # good for 4 GB of ram!
ax = fig.add_subplot(111, projection='3d')
ax.voxels(ct[::n, ::n, ::n, 0], edgecolor='none', facecolors=ct[::n, ::n, ::n, :]) # here 'n' happens
ax.set(xlabel="X",ylabel="Y",zlabel="Z")
ax.view_init(elev=25, azim=90) #nice

plt.show()
# plt.savefig("dummy_first_temperatures.jpg") # use or not to use?
plt.close(fig)
plt.show()
# plt.savefig("dummy_first_temperatures.jpg") # use or not to use?
plt.close(fig)
