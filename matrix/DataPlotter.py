import numpy as np
import matplotlib.pyplot as plt
import os  # For extracting filename

# Function to extract filename without extension
def get_filename(file):
    return os.path.splitext(os.path.basename(file.name))[0]

# Reading data from file
f = open("agridData.txt")
f2 = open("gridData.txt")
f3 = open("circData.txt")
f4 = open("normData.txt")
f5 = open("normDenseData.txt")
f6 = open("normDensetranspData.txt")

data = []
for line in f:
    x, y = line.split("\t")  # Split by tab
    data.append([float(x), float(y)])  # Append to the list

data2 = []
for line in f2:
    x, y = line.split("\t")  # Split by tab
    data2.append([float(x), float(y)])  # Append to the list

data3 = []
for line in f3:
    x, y = line.split("\t")  # Split by tab
    data3.append([float(x), float(y)]) 

data4 = []
for line in f4:
    x, y = line.split("\t")  # Split by tab
    data4.append([float(x), float(y)])  # Append to the list

data5 = []
for line in f5:
    x, y = line.split("\t")  # Split by tab
    data5.append([float(x), float(y)])  # Append to the list

data6 = []
for line in f6:
    x, y = line.split("\t")  # Split by tab
    data6.append([float(x), float(y)])  # Append to the list

data = np.asarray(data)
data2 = np.asarray(data2)
data3 = np.asarray(data3)
data4 = np.asarray(data4)
data5 = np.asarray(data5)
data6 = np.asarray(data6)

# Close files
f.close()
f2.close()
f3.close()
f4.close()
f5.close()
f6.close()

# Plotting the data with legends based on filenames
plt.plot(data[:, 0], data[:, 1], label="Rod geometry")
plt.plot(data2[:, 0], data2[:, 1], c='r', label="Grid geometry")
plt.plot(data3[:, 0], data3[:, 1], c='g', label="Descending circles geometry")
plt.plot(data4[:, 0], data4[:, 1], c='b', label="Few fin geometry")
plt.plot(data5[:, 0], data5[:, 1], c='black', label="Dense short fin geometry")
plt.plot(data6[:, 0], data6[:, 1], c='m', label="Dense long fin geometry")

# Adding title and legend
plt.title("Different Geometries Time Series")
plt.legend()  # Add legend to the plot
plt.xlabel('Time [s]')
plt.ylabel("Heat flux as quality factor")
# Show plot
plt.show()
