import numpy as np
from PIL import Image
import math
from tqdm import tqdm
import warnings
warnings.simplefilter('error')
# copper
c_p = 385.0 # copper: J/(kg*K)
k=401.0 # copper: W/(m* K)
rho=8850.0 # 1kg/m**3
c=np.float128(k/(rho*c_p))
# water
c_p2 = 4187.0 # water: J/(kg*K)
k2=0.5918 # copper: W/(m* K)
rho2=999.0# 1kg/m**3
cwt=np.float128(k2/(rho2*c_p2))

c_interface=np.float128((c*cwt)/c+cwt)

scaling_factor_m=1# cause of overflows


x_pixels=200 # 3.5 cm
y_pixels=400 # 7 cm
z_heigth=5 # in greyscale, but also in 0.1 mm. aha, its fin heigth
b_thick=5 # in greyscale, but also in 0.1 mm. aha, its plate thickness

dt=100 # time step in seconds

geometry_filepath = f"cooler2.jpg" # CHECK 111 times. it should be an image,\
# \that pillow can open
# fin_no= 10
temp_max=350.15 # kelvins
temp_ambient=293.15 #kelvins, room temp of copper

spacing=6 # spacing in pixels, also in 0.1 mm

def create_geometry(x_size,y_size,fin_heigth,base_thickness,spacing):
    img_array=np.zeros((x_size,y_size),dtype=np.float64)

    print("Generating basic geometry:")
    for i in tqdm(range(len(img_array))):
        for j in range(len(img_array[0])):
            img_array[i,j]+=base_thickness
            # if (i==len(img_array)//2) and (j>len(img_array[0])//6) and (j<len(img_array[0])//3):
            if (i>(len(img_array)//2-len(img_array)//4) and i < (len(img_array)//2+len(img_array)//4)) and (j>(len(img_array[0])//2-len(img_array[0])//4) and j < (len(img_array[0])//2+len(img_array[0])//4)) and (i%spacing<=3):
                
                img_array[i,j]+=fin_heigth
    return np.asanyarray(img_array,dtype=np.int8)

def voxelize_2Darray(array):
    max_h=np.max(array)
    geometry=np.zeros((len(array),len(array[0]),int(max_h+2)))
    print("Voxelizing...")
    for x in tqdm(range(len(geometry))):
        for y in range(len(geometry[0])):
            for z in range(len(geometry[0,0])):
                if array[x,y]>z:
                    geometry[x,y,z]+=1.0
                if array[x,y]==z:
                    geometry[x,y,z]+=0.5

    return geometry


try:
    geometry1 = Image.open(geometry_filepath)
except FileNotFoundError as e:
    geometry1=create_geometry(x_size=x_pixels,y_size=y_pixels,fin_heigth=z_heigth,base_thickness=b_thick,spacing=spacing)
    # image=Image.fromarray(geometry1.astype(np.int8),mode='L')
    # image.show()
    # plt.contourf(geometry1)
    # plt.show()

geometry1=np.asanyarray(geometry1,dtype=np.float64)
geometry=voxelize_2Darray(geometry1)

# ===========================================================================
# ============TEMP INIT======================================================
print("Temperature initialization...")
temperatures=np.zeros_like(geometry)

for k in tqdm(range(len(geometry[0,0]))):
    for i in range(len(geometry)):
        for j in range(len(geometry[0])):
            # if ((k<1) and (geometry[i,j,k]>0.5)) and (i>(x_pixels//2-x_pixels//3) and i < (x_pixels//2+x_pixels//3)and j>(y_pixels//2-y_pixels//3) and j < (y_pixels//2+y_pixels//3)): # the temperature of the base: the heater...
            #     temperatures[i,j,k]+=temp_max
            # elif ((k<1) and (geometry[i,j,k]>0.5)) and not (i>(x_pixels//2-x_pixels//3) and i < (x_pixels//2+x_pixels//3)and j>(y_pixels//2-y_pixels//3) and j < (y_pixels//2+y_pixels//3)): # the temperature of the base: not the heater...
            #     temperatures[i,j,k]+=temp_ambient
            # elif ((k>=1) and (geometry[i,j,k]>0.5)):
            #     temperatures[i,j,k]+=temp_ambient
            # elif (geometry[i,j,k]<0.1):
            #     temperatures[i,j,k]+=temp_ambient
            # else:
            temperatures[i,j,k]+=temp_ambient
                

# c=1.0 # c=(k/(rho*c_p))
np.save(f"temp_0.npy",temperatures)
np.save(f"geometry.npy",geometry)
# print(np.shape(temperatures))
'''
[1.7320508075688772, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.0, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.0, 1.4142135623730951, 1.0, 1.0, 1.4142135623730951, 1.0, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.0, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.7320508075688772]

[[-1, -1, -1], [-1, -1, 0], [-1, -1, 1], [-1, 0, -1], [-1, 0, 0], [-1, 0, 1], [-1, 1, -1], [-1, 1, 0], [-1, 1, 1], [0, -1, -1], [0, -1, 0], [0, -1, 1], [0, 0, -1], [0, 0, 1], [0, 1, -1], [0, 1, 0], [0, 1, 1], [1, -1, -1], [1, -1, 0], [1, -1, 1], [1, 0, -1], [1, 0, 0], [1, 0, 1], [1, 1, -1], [1, 1, 0], [1, 1, 1]]

'''
time=0.0
# ========================integrating part=======================================
# voxel_neighbors=[[-1,-1,-1],[0,-1,-1],[1,-1,-1],[-1,0,-1],[0,0,-1],[1,0,-1],[-1,1,-1],[0,1,-1],[1,1,-1]] # always look down!!!!
# water_neighbors_full=[[-1,-1,-1],[0,-1,-1],[1,-1,-1],[-1,0,-1],[0,0,-1],[1,0,-1],[-1,1,-1],[0,1,-1],[1,1,-1]]
# water_neighbors_full=[[-1,-1,0],[0,-1,0],[1,-1,0],[-1,0,0],[0,0,0],[1,0,0],[-1,1,0],[0,1,0],[1,1,0],[-1,-1,1],[0,-1,1],[1,-1,1],[-1,0,1],[0,0,1],[1,0,1],[-1,1,1],[0,1,0],[1,1,1]]
# distances=[1.7320508075688772, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.0, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.7320508075688772]
# water_distances_full=[1.7320508075688772, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.0, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.7320508075688772]
# water_distances_full=[1.4142135623730951, 1.4142135623730951, 1.4142135623730951, 1.4142135623730951, 1.0, 1.4142135623730951, 1.4142135623730951, 1.4142135623730951, 1.4142135623730951,1.7320508075688772, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.0, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.7320508075688772]
water_distances_full=[1.732, 1.414, 1.732, 1.414, 1.0, 1.414, 1.732, 1.414, 1.732, 1.414, 1.0, 1.414, 1.0, 1.0, 1.414, 1.0, 1.414, 1.732, 1.414, 1.732, 1.414, 1.0, 1.414, 1.732, 1.414, 1.732]
# areas_full=[0.33333333333333337, 0.4999999999999999, 0.33333333333333337, 0.4999999999999999, 1.0, 0.4999999999999999, 0.33333333333333337, 0.4999999999999999, 0.33333333333333337]
areas_full=np.asanyarray([0.333, 0.5, 0.333, 0.5, 1.0, 0.5, 0.333, 0.5, 0.333, 0.5, 1.0, 0.5, 1.0, 1.0, 0.5, 1.0, 0.5, 0.333, 0.5, 0.333, 0.5, 1.0, 0.5, 0.333, 0.5, 0.333])
# print(areas_full)
water_neighbors_full=[[-1, -1, -1], [-1, -1, 0], [-1, -1, 1], [-1, 0, -1], [-1, 0, 0], [-1, 0, 1], [-1, 1, -1], [-1, 1, 0], [-1, 1, 1], [0, -1, -1], [0, -1, 0], [0, -1, 1], [0, 0, -1], [0, 0, 1], [0, 1, -1], [0, 1, 0], [0, 1, 1], [1, -1, -1], [1, -1, 0], [1, -1, 1], [1, 0, -1], [1, 0, 0], [1, 0, 1], [1, 1, -1], [1, 1, 0], [1, 1, 1]]
# print(len(water_distances_full))
area=4 * (x_pixels // 2 + x_pixels // 3) * (y_pixels // 2 + y_pixels // 3)/scaling_factor_m**2
temp_inc=300* dt / (rho * c_p)
while True:
    # temp_inc=300* dt / (rho/1000.0 * c_p)
    heats = []
    for a in range(len(geometry)):
        for b in range(len(geometry[0])):
            if ((geometry[a, b, 0] > 0.5) and 
                (x_pixels // 2 - x_pixels // 3 < a < x_pixels // 2 + x_pixels // 3) and 
                (y_pixels // 2 - y_pixels // 3 < b < y_pixels // 2 + y_pixels // 3)):
                temperatures[a, b, 0]+=temp_inc # 30 W * t / (m**3 * rho * c_p) -> [K]
    try:
        for z in tqdm(range(1, len(geometry[0, 0]) - 1)):


            for x in range(1, len(geometry) - 1):
                for y in range(1, len(geometry[0]) - 1):
                    
                    sum_heat = 0.0
                    su1=0.0
                    su2=0.0
                    heat=0.0
                    
                    for i in range(len(water_distances_full)):
                        if geometry[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]] > 0.5:
                            a = temperatures[x, y, z]
                            b = temperatures[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]]
                            distance = water_distances_full[i]

                            sum_heat += c * dt * (np.divide(a**2 - 2 * a * b + b**2, distance**2))
                        temperatures[x, y, z] +=sum_heat
                    
                    
                    
                        if geometry[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]] == 0.5:
                            # heat=c_interface * np.float128(areas_full[i]) * (np.float128(temperatures[x, y, z]) - np.float128(temperatures[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]]) / np.float128((water_distances_full[i])))
                        
                            su1 -= c_interface * areas_full[i] *np.divide(np.subtract(temperatures[x, y, z],temperatures[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]]),(water_distances_full[i]/10.0))
                            heat = c_interface * areas_full[i] * np.divide(np.subtract(temperatures[x, y, z],temperatures[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]]),(water_distances_full[i]/10.0))

                            # Update temperatures
                            np.subtract(temperatures[x, y, z],np.divide(heat, rho/1000.0 * c_p))
                            temperatures[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]] = temp_ambient

                        heats.append(su1)


                        if geometry[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]] < 0.4:
                            for j in range(len(water_distances_full)):
                                # su2 += cwt*dt*np.power(np.divide(np.subtract(temperatures[x, y, z],temperatures[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]]),(water_distances_full[i]/10.0)),2)
                                # print(f"su2: {su2}")
                                a = temperatures[x, y, z]
                                b = temperatures[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]]
                                distance = water_distances_full[i]

                                su2+= cwt * dt * (np.divide(a**2 - 2 * a * b + b**2, distance**2))
                            temperatures[x, y, z] += np.float128(su2)
                        

        if math.isnan(np.min(temperatures)) or math.isnan(np.max(temperatures)) or math.isnan(np.sum(np.asanyarray(heats))):
            break     
        print(np.min(temperatures),np.max(temperatures),temperatures[len(temperatures)//2,len(temperatures[0])//2,len(temperatures[0,0])//2])
        time+=dt
        
        np.save(f"temperatures.npy",temperatures)

        print(f"saved at time = {time:.4f}")
        if np.sum(np.asanyarray(heats)) != 0.0:
            np.save(f"HEAT_TRANSFER_heats_{time}.npy",np.sum(np.asanyarray(heats)))
            print(f"saved at time = {time:.4f}")
            print(np.sum(np.asanyarray(heats)))
    except RuntimeWarning as e:
        print(e)
        print([x,y,z])
        print(temperatures[x,y,z])
        for i in range(len(water_distances_full)):
            print(temperatures[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]],[x + water_neighbors_full[i][0], y + water_neighbors_full[i][1], z + water_neighbors_full[i][2]])
        break
