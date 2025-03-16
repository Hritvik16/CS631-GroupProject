#ifndef GRAPH_PARTITION_H
#define GRAPH_PARTITION_H

#include <vector>
#include <eigen3/Eigen/Dense>

struct Partition {
    std::vector<int> vertices;
    Eigen::MatrixXd adjacency;
};

#endif // GRAPH_PARTITION_H
