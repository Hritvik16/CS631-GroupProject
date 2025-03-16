#ifndef IO_OPERATIONS_H
#define IO_OPERATIONS_H

#include <eigen3/Eigen/Dense>
#include <string>
#include <vector>
#include "graph_partition.h"

// Reads an adjacency matrix from a file
Eigen::MatrixXd readAdjacencyMatrix(const std::string& filename);

// Writes the partitions to an output file
void writePartitionsToFile(const std::vector<Partition>& partitions, const std::string& filename);

void printPartitionStatistics(const Partition& partition);

void printAllPartitionsStatistics(const std::vector<Partition>& partitions);

#endif // IO_OPERATIONS_H
