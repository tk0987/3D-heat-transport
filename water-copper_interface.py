import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
from tqdm import tqdm
# copper
c_p = 385 # copper: J/(kg*K)
k=401 # copper: W/(m* K)
rho=8850 # kg/m**3
c=(k/(rho*c_p))
# water
c_p2 = 4187 # water: J/(kg*K)
k2=0.5918 # copper: W/(m* K)
rho2=999# kg/m**3
cwt=(k2/(rho2*c_p2))



x_pixels=350 # 3.5 cm
y_pixels=700 # 7 cm
z_heigth=5 # in greyscale, but also in 0.1 mm. aha, its fin heigth
b_thick=5 # in greyscale, but also in 0.1 mm. aha, its plate thickness

dt=0.05 # time step in seconds

geometry_filepath = f"cooler2.jpg" # CHECK 111 times. it should be an image,\
# \that pillow can open
# fin_no= 10
temp_max=350.15 # kelvins
temp_ambient=293.15 #kelvins, room temp of copper

spacing=6 # spacing in pixels, also in 0.1 mm

def create_geometry(x_size,y_size,fin_heigth,base_thickness,spacing):
    img_array=np.zeros((x_size,y_size),dtype=np.float16)

    print("Generating basic geometry:")
    for i in tqdm(range(len(img_array))):
        for j in range(len(img_array[0])):
            img_array[i,j]+=base_thickness
            # if (i==len(img_array)//2) and (j>len(img_array[0])//6) and (j<len(img_array[0])//3):
            if i>(len(img_array)//2-len(img_array)//4) and i < (len(img_array)//2+len(img_array)//4)and j>(len(img_array[0])//2-len(img_array[0])//4) and j < (len(img_array[0])//2+len(img_array[0])//4) and (i%spacing<=3):
                
                img_array[i,j]+=fin_heigth
    return img_array

def voxelize_2Darray(array):
    max_h=np.max(array)
    geometry=np.zeros((len(array),len(array[0]),int(max_h*2.0+1)))
    print("Voxelizing...")
    for x in tqdm(range(len(geometry))):
        for y in range(len(geometry[0])):
            for z in range(len(geometry[0,0])):
                if array[x,y]>z:
                    geometry[x,y,z]+=1.0

    return geometry


try:
    geometry1 = Image.open(geometry_filepath)
except FileNotFoundError as e:
    geometry1=create_geometry(x_size=x_pixels,y_size=y_pixels,fin_heigth=z_heigth,base_thickness=b_thick,spacing=spacing)
    # image=Image.fromarray(geometry1,mode='L')
    # image.show()
    # plt.contourf(geometry1)
    # plt.show()

geometry1=np.asanyarray(geometry1,dtype=np.float16)
geometry=voxelize_2Darray(geometry1)

# ===========================================================================
# ============TEMP INIT======================================================
print("Temperature initialization...")
temperatures=np.zeros_like(geometry)

for k in tqdm(range(len(geometry[0,0]))):
    for i in range(len(geometry)):
        for j in range(len(geometry[0])):
            if k<1 and geometry[i,j,k]>0.5 and i>(x_pixels//2-x_pixels//3) and i < (x_pixels//2+x_pixels//3)and j>(y_pixels//2-y_pixels//3) and j < (y_pixels//2+y_pixels//3): # the temperature of the base: the heater...
                temperatures[i,j,k]+=temp_max
            if k<1 and geometry[i,j,k]>0.5 and not (i>(x_pixels//2-x_pixels//3) and i < (x_pixels//2+x_pixels//3)and j>(y_pixels//2-y_pixels//3) and j < (y_pixels//2+y_pixels//3)): # the temperature of the base: not the heater...
                temperatures[i,j,k]+=temp_ambient
            if k>=1 and geometry[i,j,k]>0.5:
                temperatures[i,j,k]+=temp_ambient
            if geometry[i,j,k]<0.1:
                temperatures[i,j,k]+=temp_ambient
                

# c=1.0 # c=(k/(rho*c_p))
np.save(f"temp_0.npy",temperatures)
np.save(f"geometry.npy",geometry)
# print(np.shape(temperatures))

time=0.0
# ========================integrating part=======================================
# voxel_neighbors=[[-1,-1,-1],[0,-1,-1],[1,-1,-1],[-1,0,-1],[0,0,-1],[1,0,-1],[-1,1,-1],[0,1,-1],[1,1,-1]] # always look down!!!!
voxel_neighbors=[[-1,-1,-1],[0,-1,-1],[1,-1,-1],[-1,0,-1],[0,0,-1],[1,0,-1],[-1,1,-1],[0,1,-1],[1,1,-1]]
distances=[1.7320508075688772, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.0, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.7320508075688772]
water_distances_full=[1.7320508075688772, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.0, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.0, 1.4142135623730951, 1.0, 1.0, 1.4142135623730951, 1.0, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.4142135623730951, 1.7320508075688772, 1.4142135623730951, 1.7320508075688772]
water_neighbors_full=[[-1,-1,-1],[0,-1,-1],[1,-1,-1],[-1,0,-1],[0,0,-1],[1,0,-1],[-1,1,-1],[0,1,-1],[1,1,-1],\
    [-1,-1,0],[0,-1,0],[1,-1,0],[-1,0,0],[1,0,0],[-1,1,0],[0,1,0],[1,1,0],\
        [-1,-1,1],[0,-1,1],[1,-1,1],[-1,0,1],[1,0,1],[-1,1,1],[0,1,1],[1,1,1]]
while time<=60.0:
    for z in tqdm(range(1,len(geometry[0,0])-1,1)):
        for x in range(1,len(geometry)-1,1):
            for y in range(1,len(geometry[0])-1,1):
# ____coordinates to check section____
            #    ======= COPPER PART =====
                # print("copper")
                sum=0.0

                ii=0
                if geometry[x,y,z]>0.6:

                    for i in range(len(distances)):
                        if geometry[x+voxel_neighbors[i][0],y+voxel_neighbors[i][1],z+voxel_neighbors[i][2]]>0.5:
                            sum+=temperatures[x+voxel_neighbors[i][0],y+voxel_neighbors[i][1],z+voxel_neighbors[i][2]]/distances[i]
                            
                            ii+=1
                    temperatures[x,y,z]+=c*(sum-(ii)*temperatures[x,y,z])*dt*10000
                    #    ======= COPPER/WATER PART =====
                sum2=0.0
                ii2=0
                # print("water/copper")
                if geometry[x,y,z]<0.5:

                    for i1 in range(len(water_distances_full)):
                        if geometry[x+water_neighbors_full[i1][0],y+water_neighbors_full[i1][1],z+water_neighbors_full[i1][2]]>0.5:
                            sum2+=temperatures[x+water_neighbors_full[i1][0],y+water_neighbors_full[i1][1],z+water_neighbors_full[i1][2]]/water_distances_full[i1]
                            ii2+=1
                    temperatures[x,y,z]+=c*cwt/(cwt+c)*(sum2-(ii2)*temperatures[x,y,z])*dt*10000
                #    ======= WATER PART =====
                    sum21=0.0
                    ii21=0
                    # print("water")
                    for i in range(len(distances)):
                        if geometry[x+voxel_neighbors[i][0],y+voxel_neighbors[i][1],z+voxel_neighbors[i][2]]<0.5:
                            sum21+=temperatures[x+voxel_neighbors[i][0],y+voxel_neighbors[i][1],z+voxel_neighbors[i][2]]/distances[i]
                            ii21+=1
                    temperatures[x,y,z]+=cwt*(sum21-(ii21)*temperatures[x,y,z])*dt*10000             


    time+=dt
    # print(time)
    # if abs(time%1)<=(0.4):
    # try:
    np.save(f"temperatures_time_{time:.4f}.npy",temperatures)

    print(f"saved at time = {time:.4f}")
