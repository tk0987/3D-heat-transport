import numpy as np
import matplotlib.pyplot as plt

# Reading data from file
f = open("geoagrid.txt")
data = []
for line in f:
    x, y, z = line.split("\t")  # Split by tab
    data.append([float(x),float(y),float(z)])  # Append to the list

# Convert list to NumPy array
data = np.asarray(data)

# Reshape the data into an image with shape (200, 400, 3)
k=0
image_data = np.zeros(shape=(200,400,1))
for i in range(len(image_data)):
	for j in range(len(image_data[0])):
		image_data[i,j,0]+=data[k,2]
		k+=1

# Normalize the data to [0, 1] range for proper display (optional step depending on data)
image_data = (image_data - np.min(image_data)) / (np.max(image_data) - np.min(image_data))

# Display the image
plt.imshow(image_data)
plt.title("Geonorm Image")
plt.show()
