#ifndef CONFIG_H
#define CONFIG_H

#include <string>

std::string INPUT_FILE = "../datasets/dataset_1000_cities/adjacency_matrix.txt";
constexpr int NUM_PARTITIONS = 4;
std::string OUTPUT_FILE = "partitions.txt";

#endif // CONFIG_H