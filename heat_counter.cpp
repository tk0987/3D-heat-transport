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
            for (int zz = 0; zz <= static_cast<int>(z); zz++) {
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
const double dt = 1;

// Temperature settings
const double temp_max = 350.15;
const double temp_ambient = 293.15;

// Spacing
const int spacing = 6;
const int b_thick=2;
const int z_height=5;
const int x_pixels=200;
const int y_pixels=400;
// Time initialization
double t = 0.0;

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
// Calculation of temperature increment
double temp_inc = 20000 * dt / (rho * c_p);

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
    double heat;
    while(!isnan(total_heat)){
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
        double heat_exchange = 0.0;

        for (int z = 1; z < geometry[0][0].size() - 1; z++) {
            for (int x = 1; x < geometry.size() - 1; x++) {
                for (int y = 1; y < geometry[0].size() - 1; y++) {
                if ((geometry[x][y][z] > 0.5) 
                    && (temperatures[x+1][y][z] > 0.5) 
                    && (temperatures[x-1][y][z] > 0.5) 
                    && (temperatures[x][y+1][z] > 0.5) 
                    && (temperatures[x][y-1][z] > 0.5)
                    && (temperatures[x][y][z+1] > 0.5)
                    && (temperatures[x][y][z-1] > 0.5)) {
                    
                    int trueConditions = 0;
                    if (temperatures[x+1][y][z] > 0.5) trueConditions++;
                    if (temperatures[x-1][y][z] > 0.5) trueConditions++;
                    if (temperatures[x][y+1][z] > 0.5) trueConditions++;
                    if (temperatures[x][y-1][z] > 0.5) trueConditions++;
                    if (temperatures[x][y][z+1] > 0.5) trueConditions++;
                    if (temperatures[x][y][z-1] > 0.5) trueConditions++;

                    double laplacian = (
                        (temperatures[x+1][y][z] > 0.5 ? temperatures[x+1][y][z] : 0) +
                        (temperatures[x-1][y][z] > 0.5 ? temperatures[x-1][y][z] : 0) +
                        (temperatures[x][y+1][z] > 0.5 ? temperatures[x][y+1][z] : 0) +
                        (temperatures[x][y-1][z] > 0.5 ? temperatures[x][y-1][z] : 0) +
                        (temperatures[x][y][z+1] > 0.5 ? temperatures[x][y][z+1] : 0) +
                        (temperatures[x][y][z-1] > 0.5 ? temperatures[x][y][z-1] : 0) -
                        trueConditions * temperatures[x][y][z]
                    );

                    new_temperatures[x][y][z] += alpha * laplacian * dt;
                }


                    // Idealistic heat exchange with adjacent water (if adjacent to water)
                    for (size_t i = 0; i < water_neighbors_full.size(); i++) {
                        int nx = x + water_neighbors_full[i][0];
                        int ny = y + water_neighbors_full[i][1];
                        int nz = z + water_neighbors_full[i][2];
                        
                        if (geometry[nx][ny][nz] == 0.5) {  // Assuming water exists in half-voxel
                            double temp_diff = temperatures[x][y][z] - temperatures[nx][ny][nz];
                            double heat_transfer = c_interface * areas_full[i] * temp_diff / water_distances_full[i];
                            heat_exchange += heat_transfer;
                            new_temperatures[x][y][z] -= heat_transfer / (rho * c_p);
                            new_temperatures[nx][ny][nz] =temp_ambient;  // Water temperature adjustment
                        }
                    }
                }
            }
        }

        temperatures = new_temperatures;
        t += dt;
        total_heat += heat_exchange;

        // Print time and heat
        print("Time: " + to_string(t) + "s, Heat: " + to_string(total_heat) + " J");
    }}

    return 0;
}
