# Spectral Graph Partitioning

This repository contains a C++ implementation of spectral graph partitioning. The project uses spectral methods to partition a graph into multiple subgraphs by computing the Laplacian matrix and extracting the Fiedler vector (the second smallest eigenvector). It leverages parallel processing via OpenMP for efficient computation and is structured into multiple files for modularity and maintainability.

## File Structure

- **config.h:**  
  Contains configuration constants
  Change config to change number of partitions, input adjacency matrix file and output file name

- **graph_partition.h:**  
  Contains the shared definition of the `Partition` structure, which holds vertex indices and the corresponding sub-adjacency matrix.

- **io_operations.h / io_operations.cpp:**  
  Functions to read the adjacency matrix from a file and write the partition results to an output file.

- **laplacian_eigen.h / laplacian_eigen.cpp:**  
  Functions to compute the Laplacian matrix and the Fiedler vector using eigenvalue decomposition.

- **spectral_operations.h / spectral_operations.cpp:**  
  Implements the spectral partitioning operations (including graph bisection and parallel partitioning).

- **main.cpp:**  
  The main entry point that sets up the program, reads the graph, performs partitioning, prints statistics, and writes the output.

## Dependencies

- **C++ Compiler**

- **Eigen:**  
  A C++ template library for linear algebra.

  ```bash
    sudo apt install libeigen3-dev
  ```

- **OpenMP**

## Building the Project

Ensure that the Eigen library is installed on your system and update the include path accordingly. Compile the project using the following command:

```bash
make

./spectral_partitioning
```
