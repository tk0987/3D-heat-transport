import numpy as np
from PIL import Image
# import matplotlib.pyplot as plt
from tqdm import tqdm
# import math
import warnings

warnings.simplefilter('error')

# Constants for copper
c_p = 385.0  # J/(kg*K)
k = 401.0  # W/(m*K)
rho = 8850.0  # kg/m^3
c = k / (rho * c_p)

# Constants for water
c_p2 = 4187.0  # J/(kg*K)
k2 = 0.5918  # W/(m*K)
rho2 = 999.0  # kg/m^3
cwt = k2 / (rho2 * c_p2)

c_interface = (c * cwt) / (c + cwt)
scaling_factor_m = 100  # Scaling to prevent overflow

# Geometry parameters
x_pixels = 200
y_pixels = 400
z_height = 5
b_thick = 5
dt = 100.0  # Time step in seconds
temp_max = 350.15  # Maximum temperature in Kelvin
temp_ambient = 293.15  # Ambient temperature in Kelvin
spacing = 6  # Spacing in pixels

# Geometry creation function
def create_geometry(x_size, y_size, fin_height, base_thickness, spacing):
    img_array = np.zeros((x_size, y_size), dtype=np.float64)

    print("Generating basic geometry:")
    for i in tqdm(range(x_size)):
        for j in range(y_size):
            img_array[i, j] += base_thickness
            if (i > x_size // 2 - x_size // 4) and (i < x_size // 2 + x_size // 4) and (j > y_size // 2 - y_size // 4) and (j < y_size // 2 + y_size // 4) and (i % spacing <= 3):
                img_array[i, j] += fin_height

    return img_array.astype(np.int8)

# Voxelization function
def voxelize_2Darray(array):
    max_h = np.max(array)
    geometry = np.zeros((len(array), len(array[0]), int(max_h + 1)), dtype=np.float64)

    print("Voxelizing...")
    for x in tqdm(range(len(geometry))):
        for y in range(len(geometry[0])):
            for z in range(len(geometry[0, 0])):
                if array[x, y] > z:
                    geometry[x, y, z] += 1.0
                elif array[x, y] == z:
                    geometry[x, y, z] += 0.5

    return geometry

# Load or create geometry
try:
    geometry1 = Image.open("cooler2.jpg")
except FileNotFoundError:
    geometry1 = create_geometry(x_size=x_pixels, y_size=y_pixels, fin_height=z_height, base_thickness=b_thick, spacing=spacing)

geometry1 = np.asarray(geometry1, dtype=np.float64)
geometry = voxelize_2Darray(geometry1)

# Temperature initialization
print("Temperature initialization...")
temperatures = np.full_like(geometry, temp_ambient, dtype=np.float64)

# Heat transfer constants
water_distances_full = [1.732, 1.414, 1.732, 1.414, 1.0, 1.414, 1.732, 1.414, 1.732, 1.414, 1.0, 1.414, 1.0, 1.0, 1.414, 1.0, 1.414, 1.732, 1.414, 1.732, 1.414, 1.0, 1.414, 1.732, 1.414, 1.732]
areas_full = [0.333, 0.5, 0.333, 0.5, 1.0, 0.5, 0.333, 0.5, 0.333, 0.5, 1.0, 0.5, 1.0, 1.0, 0.5, 1.0, 0.5, 0.333, 0.5, 0.333, 0.5, 1.0, 0.5, 0.333, 0.5, 0.333]
water_neighbors_full = [[-1, -1, -1], [-1, -1, 0], [-1, -1, 1], [-1, 0, -1], [-1, 0, 0], [-1, 0, 1], [-1, 1, -1], [-1, 1, 0], [-1, 1, 1], 
                                 [0, -1, -1], [0, -1, 0], [0, -1, 1], [0, 0, -1], [0, 0, 1], [0, 1, -1], [0, 1, 0], [0, 1, 1], 
                                 [1, -1, -1], [1, -1, 0], [1, -1, 1], [1, 0, -1], [1, 0, 0], [1, 0, 1], [1, 1, -1], [1, 1, 0], [1, 1, 1]]

area = 4 * (x_pixels // 2 + x_pixels // 3) * (y_pixels // 2 + y_pixels // 3) / scaling_factor_m ** 2
temp_inc = 300 * dt / (rho * c_p) # 300 [W]
time = 0.0
heats1=[]
# Time integration loop
while True:
    heats = []
    for a in range(len(geometry)):
        for b in range(len(geometry[0])):
            if geometry[a, b, 0] > 0.5:
                temperatures[a, b, 0] = np.clip(temperatures[a, b, 0] + temp_inc, temp_ambient, temp_max)

    try:
        for z in tqdm(range(1, len(geometry[0, 0]) - 1)):
            for x in range(1, len(geometry) - 1):
                for y in range(1, len(geometry[0]) - 1):
                    sum_heat = 0.0
                    
                    for i in range(len(water_distances_full)):
                        if geometry[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]] > 0.5:
                            a = temperatures[x, y, z]
                            b = temperatures[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]]
                            distance = water_distances_full[i]
                            
                            delta_temp = np.subtract(a, b)
                            sum_heat += c * dt * (delta_temp**2) / (distance**2)
                            
                    temperatures[x, y, z] += sum_heat

                    for i in range(len(water_distances_full)):
                        if (geometry[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]] == 0.5):
                            delta_temp = np.subtract(temperatures[x, y, z], temperatures[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]])
                            heat = c_interface * areas_full[i] * delta_temp / water_distances_full[i]
                            temperatures[x, y, z] -= heat / (rho * c_p)
                            temperatures[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]] = temp_ambient

                            heats.append(heat)
                    
        sth=np.sum(heats)
        heats1.append(sth)
        if np.isnan(np.min(temperatures)) or np.isnan(np.max(temperatures)):
            break
        if sth>0:
            np.save("heats_new.npy",heats1)
            print(f"saved at: {time} [s]")
        print(np.min(temperatures), np.max(temperatures), temperatures[len(temperatures)//2, len(temperatures[0])//2, len(temperatures[0, 0])//2],[sth,time])
        time += dt
    except FloatingPointError:
        print(f'FloatingPointError at time step {time} seconds')
        break

# plt.imshow(temperatures[:, :, 2], cmap='hot', interpolation='nearest')
# plt.colorbar()
# plt.show()
