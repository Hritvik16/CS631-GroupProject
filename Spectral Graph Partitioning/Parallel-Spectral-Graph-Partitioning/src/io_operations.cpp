#include "../include/io_operations.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <cmath>
#include "../include/graph_partition.h"

Eigen::MatrixXd readAdjacencyMatrix(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error opening file: " << filename << std::endl;
        exit(1);
    }
    
    std::string line;
    std::vector<double> all_values;
    
    while (std::getline(file, line)) {
        std::istringstream iss(line);
        double val;
        while (iss >> val) {
            all_values.push_back(val);
        }
    }
    
    int n = static_cast<int>(std::sqrt(all_values.size()));
    
    if (n * n != all_values.size()) {
        std::cerr << "Warning: Data doesn't form a perfect square matrix. Found " 
                  << all_values.size() << " values, nearest square is " << n << "×" << n << std::endl;
    }
    
    Eigen::MatrixXd adjacency = Eigen::MatrixXd::Zero(n, n);
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            int index = i * n + j;
            if (index < all_values.size()) {
                adjacency(i, j) = all_values[index];
            }
        }
    }
    
    return adjacency;
}

void writePartitionsToFile(const std::vector<Partition>& partitions, const std::string& filename) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error opening output file: " << filename << std::endl;
        return;
    }
    
    // file << "Number of partitions: " << partitions.size() << std::endl;
    
    for (int i = 0; i < partitions.size(); ++i) {
        // file << "Partition " << i << " (size " << partitions[i].vertices.size() << "): ";
        for (int vertex : partitions[i].vertices) {
            file << vertex << " ";
        }
        file << std::endl;
    }
    
    file.close();
}




// Function to compute statistics for a given partition
void printPartitionStatistics(const Partition& partition) {
    int n = partition.vertices.size();
    int internalEdges = 0;
    double totalDegree = 0.0;
    
    // For an undirected graph, count each edge only once.
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (partition.adjacency(i, j) != 0) {
                internalEdges++;
            }
        }
        // Compute vertex degree (sum of row entries)
        totalDegree += partition.adjacency.row(i).sum();
    }
    
    double avgDegree = (n > 0) ? totalDegree / n : 0;
    double density = (n > 1) ? (2.0 * internalEdges) / (n * (n - 1)) : 0;
    
    std::cout << "Partition Size: " << n << "\n";
    std::cout << "Internal Edges: " << internalEdges << "\n";
    std::cout << "Average Degree: " << avgDegree << "\n";
    std::cout << "Density: " << density << "\n";
}

// Example of iterating over partitions and printing their statistics:
void printAllPartitionsStatistics(const std::vector<Partition>& partitions) {
    for (size_t i = 0; i < partitions.size(); ++i) {
        std::cout << "Statistics for Partition " << i << ":\n";
        printPartitionStatistics(partitions[i]);
        std::cout << "---------------------------\n";
    }
}