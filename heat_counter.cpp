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
const long double c = k / (rho * c_p);

// Water properties
const double c_p2 = 4187.0;
const double k2 = 0.5918;
const double rho2 = 999.0;
const long double cwt = k2 / (rho2 * c_p2);

// Interface diffusivity
const long double c_interface = (c * cwt) / (c + cwt);

// Scaling factor for avoiding overflows
const int scaling_factor_m = 100;

// Pixel dimensions
const int x_pixels = 200;
const int y_pixels = 400;
const int z_height = 5;
const int b_thick = 5;

// Time step in seconds
const double dt = 0.1;

// Temperature settings
const double temp_max = 350.15;
const double temp_ambient = 293.15;

// Spacing
const int spacing = 6;

// Time initialization
double t = 0.0;

// Area array
vector<double> areas_full = {0.333, 0.5, 0.333, 0.5, 1.0, 0.5, 0.333, 0.5, 0.333, 0.5, 1.0, 0.5, 1.0, 1.0, 0.5, 1.0, 0.5, 0.333, 0.5, 0.333, 0.5, 1.0, 0.5, 0.333, 0.5, 0.333};

// Water distances array
vector<double> water_distances_full = {1.732, 1.414, 1.732, 1.414, 1.0, 1.414, 1.732, 1.414, 1.732, 1.414, 1.0, 1.414, 1.0, 1.0, 1.414, 1.0, 1.414, 1.732, 1.414, 1.732, 1.414, 1.0, 1.414, 1.732, 1.414, 1.732};

// Water neighbors 2D array
vector<array<int, 3>> water_neighbors_full = {
    {-1, -1, -1}, {-1, -1, 0}, {-1, -1, 1}, {-1, 0, -1}, {-1, 0, 0}, {-1, 0, 1}, 
    {-1, 1, -1}, {-1, 1, 0}, {-1, 1, 1}, {0, -1, -1}, {0, -1, 0}, {0, -1, 1}, 
    {0, 0, -1}, {0, 0, 1}, {0, 1, -1}, {0, 1, 0}, {0, 1, 1}, {1, -1, -1}, 
    {1, -1, 0}, {1, -1, 1}, {1, 0, -1}, {1, 0, 0}, {1, 0, 1}, {1, 1, -1}, 
    {1, 1, 0}, {1, 1, 1}
};

// Calculation of temperature increment
double temp_inc = 20000 * dt / (rho / 1000.0 * c_p);

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
    double heat = 0.0;
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

        // Heat diffusion phase
        for (int z = 1; z < geometry[0][0].size() - 1; z++) {
            for (int x = 1; x < geometry.size() - 1; x++) {
                for (int y = 1; y < geometry[0].size() - 1; y++) {
                    double sum_temp = 0.0;
                    double su1 = 0.0;

                    for (size_t i = 0; i < water_neighbors_full.size(); i++) {
                        int nx = x + water_neighbors_full[i][0];
                        int ny = y + water_neighbors_full[i][1];
                        int nz = z + water_neighbors_full[i][2];

                        if (geometry[nx][ny][nz] > 0.6) {
                            double temp_diff = temperatures[x][y][z] - temperatures[nx][ny][nz];
                            sum_temp += c * dt * temp_diff * temp_diff / (water_distances_full[i] * water_distances_full[i]);
                        }}
                          temperatures[x][y][z] += sum_temp;
                         for (size_t i = 0; i < water_neighbors_full.size(); i++) {
                        int nx = x + water_neighbors_full[i][0];
                        int ny = y + water_neighbors_full[i][1];
                        int nz = z + water_neighbors_full[i][2];
                        if (geometry[nx][ny][nz] == 0.5) {
                            double temp_diff = temperatures[x][y][z] - temperatures[nx][ny][nz];
                            su1 += c_interface * areas_full[i] * temp_diff / water_distances_full[i];
                            temperatures[x][y][z] -= su1 / (rho * c_p);
                            temperatures[nx][ny][nz] = temp_ambient;
                        }
                    }
                   

                   heat += su1;
                    
                }
            }
        }
       
        t += dt;
       print("Time: " + to_string(t));
        print("Heat: " + to_string(heat)); // 4 decimal places for heat
          }

    return 0;
}
