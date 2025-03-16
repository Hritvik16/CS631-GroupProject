#include <iostream>
#include <omp.h>
#include "include/io_operations.h"
#include "include/spectral_operations.h"
#include <eigen3/Eigen/Dense>
#include "include/config.h"

int main(int argc, char* argv[]) {
    std::string input_file = INPUT_FILE;
    int num_partitions = NUM_PARTITIONS;
    std::string output_file = OUTPUT_FILE;
    
    // Set the number of threads using OpenMP
    int num_threads = omp_get_max_threads();
    omp_set_num_threads(num_threads);
    std::cout << "Running with " << num_threads << " threads" << std::endl;
    
    // Read the adjacency matrix from file
    std::cout << "Reading adjacency matrix from " << input_file << std::endl;
    Eigen::MatrixXd adjacency = readAdjacencyMatrix(input_file);
    int n = adjacency.rows();
    std::cout << "Graph has " << n << " vertices" << std::endl;
    
    if (num_partitions > n) {
        std::cout << "Warning: Requested more partitions than vertices. Setting partitions to " << n << std::endl;
        num_partitions = n;
    }
    
    // Perform parallel spectral partitioning
    std::cout << "Performing parallel spectral partitioning into " << num_partitions << " partitions..." << std::endl;
    
    double start_time = omp_get_wtime();
    std::vector<Partition> partitions = parallelSpectralPartitioning(adjacency, num_partitions);
    double end_time = omp_get_wtime();
    
    std::cout << "Partitioning completed in " << end_time - start_time << " seconds" << std::endl;
    std::cout << "Actual number of partitions: " << partitions.size() << std::endl;


    // printAllPartitionsStatistics(partitions);
    
    // Write the partitions to the output file
    std::cout << "Writing partitions to " << output_file << std::endl;
    writePartitionsToFile(partitions, output_file);
    
    return 0;
}
