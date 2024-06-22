import numpy as np
from PIL import Image
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
from tqdm import tqdm

c_p = 385 # copper: J/(kg*K)
k=401 # copper: W/(m**2 K)
rho=8850 # kg/m**3
c=(k/(rho*c_p))
x_pixels=700 # 7 cm
y_pixels=1400 # 14 cm
z_heigth=35 # in greyscale, but also in 0.1 mm. aha, its fin heigth
b_thick=20 # in greyscale, but also in 0.1 mm. aha, its plate thickness

dt=0.05 # time step in seconds

geometry_filepath = f"C:\\Users\\TK\\Desktop\\heat\\cooler2.jpg" # CHECK 111 times. it should be an image,\
# \that pillow can open

temp_max=350.15 # kelvins
temp_ambient=293.15 #kelvins, room temp

spacing=10 # spacing in pixels, also in 0.1 mm

def create_geometry(x_size,y_size,fin_heigth,base_thickness,spacing):
    img_array=np.zeros((x_size,y_size),dtype=np.int8)

    print("Generating basic geometry:")
    for i in tqdm(range(len(img_array))):
        for j in range(len(img_array[0])):
            img_array[i,j]+=base_thickness
            if (i>200 )and (i<500) and (j>400) and (j<1000 )and (i%spacing<=3):
                # if :
                img_array[i,j]+=fin_heigth
    return img_array

def voxelize_2Darray(array):
    max_h=np.max(array)
    geometry=np.zeros((len(array),len(array[0]),int(max_h*1.5)))
    print("Voxelizing...")
    for x in tqdm(range(len(geometry))):
        for y in range(len(geometry[0])):
            for z in range(len(geometry[0,0])):
                if array[x,y]>=z:
                    geometry[x,y,z]+=1.0

    return geometry


try:
    geometry1 = Image.open(geometry_filepath)
except FileNotFoundError as e:
    geometry1=create_geometry(x_size=x_pixels,y_size=y_pixels,fin_heigth=z_heigth,base_thickness=b_thick,spacing=spacing)

geometry1=np.asanyarray(geometry1,dtype=np.float16)
geometry=voxelize_2Darray(geometry1)

# ===========================================================================
# ============TEMP INIT======================================================
print("Temperature initialization...")
temperatures=np.zeros_like(geometry)

for k in tqdm(range(len(geometry[0,0]))):
    for i in range(len(geometry)):
        for j in range(len(geometry[0])):
            if k<1 and geometry[i,j,k]>0.0 and ((i>100 )and (i<600) and (j>200) and (j<1200 )): # the temperature of the base: the heater...
                temperatures[i,j,k]+=temp_max
            if k<1 and geometry[i,j,k]>0.0 and not ((i>100 )and (i<600) and (j>200) and (j<1200 )): # the temperature of the base: not the heater...
                temperatures[i,j,k]+=temp_ambient
            if k>=1 and geometry[i,j,k]>0.0:
                temperatures[i,j,k]+=temp_ambient
# c=1.0 # c=(k/(rho*c_p))
np.save(f"C:\\Users\\TK\\Desktop\\heat\\temp_0.npy",temperatures)
np.save(f"C:\\Users\\TK\\Desktop\\heat\\geometry.npy",geometry)
# print(np.shape(temperatures))

time=0.0
# ========================integrating part=======================================
voxel_neighbors=[[-1,-1,-1],[0,-1,-1],[1,-1,-1],[-1,0,-1],[0,0,-1],[1,0,-1],[-1,1,-1],[0,1,-1],[1,1,-1]] # always look down!!!!
while time<=4.0: # seconds, my i3-4000m likes that! 1.37 it/s...
    print(str(time)+"\n")
    for z in tqdm(range(1,len(geometry[0,0])-1,1)):
        for x in range(1,len(geometry)-1,1):
            for y in range(1,len(geometry[0])-1,1):
# ____coordinates to check section____
               
                sum=0.0
                ii=0
                if geometry[x,y,z]>0.0:

                    for dx,dy,dz in voxel_neighbors:
                        if geometry[x+dx,y+dy,z+dz]>0.0:
                            sum+=temperatures[x+dx,y+dy,z+dz] # bad line - laplace op. includes division by squared distance 1e-4 [m] units. keep in mind! lazy today, maybe tommorow
                            ii+=1


                    temperatures[x,y,z]+=c*(sum-(ii)*temperatures[x,y,z])*dt*10000 # laplace ;) 
                    


    time+=dt
    print(time)
    if abs(time%1)<=0.01:
    # try:
        np.save(f"C:/Users/TK/Desktop/heat/temperatures_time_{time:.4f}.npy",temperatures)

        print(f"saved at time = {time:.4f}")
