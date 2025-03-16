#ifndef SPECTRAL_OPERATIONS_H
#define SPECTRAL_OPERATIONS_H

#include <vector>
#include <utility>
#include "graph_partition.h"
#include <eigen3/Eigen/Dense>

// Bisects a graph partition into two based on the Fiedler vector.
std::pair<Partition, Partition> bisectGraph(const Partition& graph);

// Recursively bisects the largest partition until the target number of partitions is reached.
void recursiveSpectralBisection(std::vector<Partition>& partitions, int target_partitions);

// Performs parallel spectral partitioning using a queue-based approach.
std::vector<Partition> parallelSpectralPartitioning(const Eigen::MatrixXd& adjacency, int num_partitions);

#endif // SPECTRAL_OPERATIONS_H
