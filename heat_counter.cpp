#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <array>
#include <cmath> // Needed for math functions

using namespace std;

void print(const string& a) {
    cout << a << endl;
}

vector<vector<float>> create_geometry(int x_size, int y_size, int fin_height, int base_thickness, int spacing) {
    vector<vector<float>> img_array(x_size, vector<float>(y_size, base_thickness));

    print("Generating basic geometry:");
    
    for (int i = 0; i < x_size; i++) {
        for (int j = 0; j < y_size; j++) {
            img_array[i][j] += base_thickness;
            if ((i > (x_size / 2 - x_size / 4) && i < (x_size / 2 + x_size / 4)) && 
                (j > (y_size / 2 - y_size / 4) && j < (y_size / 2 + y_size / 4)) && 
                (i % spacing <= 1)) {
                img_array[i][j] += fin_height;
            }
        }
    }
    
    return img_array;
} 

vector<vector<vector<float>>> voxelize_2Darray(const vector<vector<float>>& array, int x, int y) {
    float z = 0;
    for (const auto& row : array) {
        float max_in_row = *max_element(row.begin(), row.end());
        if (max_in_row > z) {
            z = max_in_row;
        }
    }

    vector<vector<vector<float>>> geometry(x, vector<vector<float>>(y, vector<float>(static_cast<int>(z) + 1, 0)));

    print("Voxelizing...");

    for (int xx = 0; xx < x; xx++) {
        for (int yy = 0; yy < y; yy++) {
            for (int zz = 0; zz <= static_cast<int>(1 + z); zz++) {
                if (array[xx][yy] > zz) {
                    geometry[xx][yy][zz] = 1;
                } else if (array[xx][yy] == zz) {
                    geometry[xx][yy][zz] = 0.5;
                }
            }
        }
    }

    print("Done...");
    return geometry;
}

// Copper properties
const double c_p = 385.0;
const double k = 401.0;
const double rho = 8850.0;
const long double alpha = k / (rho * c_p); // Thermal diffusivity

// Water properties (for heat exchange)
const double c_p2 = 4187.0;
const double k2 = 0.5918;
const double rho2 = 999.0;
const long double alpha2 = k2 / (rho2 * c_p2);

// Interface diffusivity
const long double c_interface = (alpha * alpha2) / (alpha + alpha2);

// Time step in seconds
const double dt = 10;

// Temperature settings
const double temp_max = 350.15;
const double temp_ambient = 293.15;

// Spacing
const int spacing = 6;
const int b_thick = 2;
const int z_height = 5;
const int x_pixels = 200;
const int y_pixels = 400;
 
// Time initialization
double t = 0.0;
double scale=1000.0;

// Area array
vector<double> areas_full = {0.333, 0.5, 0.333, 0.5, 1.0, 0.5, 0.333, 0.5, 0.333, 0.5, 1.0, 0.5, 1.0, 1.0, 0.5, 1.0, 0.5, 0.333, 0.5, 0.333, 0.5, 1.0, 0.5, 0.333, 0.5, 0.333};

// Water distances array
vector<double> water_distances_full = {1.732, 1.414, 1.732, 1.414, 1.0, 1.414, 1.732, 1.414, 1.732, 1.414, 1.0, 1.414, 1.0, 1.0, 1.414, 1.0, 1.414, 1.732, 1.414, 1.732, 1.414, 1.0, 1.414, 1.732, 1.414, 1.732};
vector<array<int, 3>> water_neighbors_full = {
    {1, 0, 0}, {-1, 0, 0}, {0, 1, 0}, {0, -1, 0}, {0, 0, 1}, {0, 0, -1}, 
    {1, 1, 0}, {1, -1, 0}, {-1, 1, 0}, {-1, -1, 0}, {0, 1, 1}, {0, -1, 1}, 
    {1, 0, 1}, {-1, 0, 1}, {0, 1, -1}, {0, -1, -1}, {1, 0, -1}, {-1, 0, -1}, 
    {1, 1, 1}, {-1, -1, 1}, {1, -1, 1}, {-1, 1, 1}, {1, 1, -1}, {-1, -1, -1}, 
    {1, -1, -1}, {-1, 1, -1}
};

// Calculation of temperature increment    /scale
double temp_inc = 100 * dt / (rho* c_p)/ (x_pixels / 2 - x_pixels / 3)/(y_pixels / 2 - y_pixels / 3);

int main() {
    // Initialize geometry and temperature arrays
    vector<vector<vector<float>>> geometry = voxelize_2Darray(create_geometry(x_pixels, y_pixels, z_height, b_thick, spacing), x_pixels, y_pixels);
    vector<vector<vector<float>>> temperatures = geometry;

    // Initialize temperatures to ambient temperature
    print("Initializing temperatures...");
    for (auto& plane : temperatures) {
        for (auto& row : plane) {
            fill(row.begin(), row.end(), temp_ambient);
        }
    }
    print("Initialization complete.");

    // Integration loop
    print("Starting integration...");
    double total_heat = 0.0;
    while (true) {
        // Energy adding phase
        for (int a = 0; a < geometry.size(); a++) {
            for (int b = 0; b < geometry[0].size(); b++) {
                if ((geometry[a][b][0] > 0.5) && 
                    (a > x_pixels / 2 - x_pixels / 3) && (a < x_pixels / 2 + x_pixels / 3) &&
                    (b > y_pixels / 2 - y_pixels / 3) && (b < y_pixels / 2 + y_pixels / 3)) {
                    temperatures[a][b][0] += temp_inc; 
                }
            }
        }

        // Heat diffusion phase using the Laplace operator
        vector<vector<vector<float>>> new_temperatures = temperatures;
       double heat=0.0;
double sheat=0.0;
double rheat=0.0;

        for (int z = 1; z < geometry[0][0].size() - 1; z++) {
            for (int x = 1; x < geometry.size() - 1; x++) {
                for (int y = 1; y < geometry[0].size() - 1; y++) {
                    if (geometry[x][y][z] > 0.5) {
                        double laplacian = 0.0;
                        int valid_neighbors = 0;


                        // Check each neighboring point and add its temperature if valid
                        if (geometry[x+1][y][z] > 0.5) {
                            laplacian += temperatures[x+1][y][z];
                            valid_neighbors++;
                        }
                        if (geometry[x-1][y][z] > 0.5) {
                            laplacian += temperatures[x-1][y][z];
                            valid_neighbors++;
                        }
                        if (geometry[x][y+1][z] > 0.5) {
                            laplacian += temperatures[x][y+1][z];
                            valid_neighbors++;
                        }
                        if (geometry[x][y-1][z] > 0.5) {
                            laplacian += temperatures[x][y-1][z];
                            valid_neighbors++;
                        }
                        if (geometry[x][y][z+1] > 0.5) {
                            laplacian += temperatures[x][y][z+1];
                            valid_neighbors++;
                        }
                        if (geometry[x][y][z-1] > 0.5) {
                            laplacian += temperatures[x][y][z-1];
                            valid_neighbors++;
                        }

                        // Adjust the Laplacian 
                       // Adjust the Laplacian to factor in only the valid neighbors
                        laplacian -= laplacian*temperatures[x][y][z];// Subtract the central point contribution

                        // Update the new temperature based on the valid neighbors
                        if (valid_neighbors > 0) {  // Only update if there are valid neighbors
                            new_temperatures[x][y][z] += alpha * laplacian * dt / valid_neighbors;
                        }

                        // Idealistic heat exchange with adjacent water (if adjacent to water)
                        double total_heat_transfer = 0.0;
                        int valid_water_neighbors = 0;  // Count the valid water neighbors

                        // Loop over all permutations of neighbor displacements for x, y, z
// Loop over all defined neighbor directions in water_neighbors_full
}

        // Update the temperatures for the next iteration
       // temperatures = new_temperatures;
heat=0.0;
rheat=0.0;

                    if (geometry[x][y][z] == 0.5) {
                        int valid_neighbors = 0;

                        // Check each neighboring point and add its temperature if valid
                        if (geometry[x-1][y][z] > 0.5) {
                            heat= c_interface*(temperatures[x-1][y][z]-temp_ambient);
                            valid_neighbors++;
                            sheat+=heat;
                           temperatures[x][y][z]-=heat/(rho*c_p);
                        }
                        
                        
                        if (geometry[x][y-1][z] > 0.5) {
                            heat= c_interface*(temperatures[x][y-1][z]-temp_ambient);
                            valid_neighbors++;
                                      sheat+=heat;
                           temperatures[x][y][z]-=heat/(rho*c_p);
                        }
                        
                        if (geometry[x][y][z-1] > 0.5) {
                            heat+= c_interface*(temperatures[x][y][z-1]-temp_ambient);
                            valid_neighbors++;
                                     sheat+=heat;
                           temperatures[x][y][z]-=heat/(rho*c_p);
                        }
                        
                        

                        
                          
                        





                    }
                }
            }
        }
        temperatures = new_temperatures;
        t += dt;
        
        // Print time and total heat exchanged
        print("Time: " + to_string(t) + "s, Heat exchange: " + to_string(sheat) + " J");

        // Optional: Break the loop if needed (e.g., time exceeds certain limit)
        
    }

    return 0;
}
