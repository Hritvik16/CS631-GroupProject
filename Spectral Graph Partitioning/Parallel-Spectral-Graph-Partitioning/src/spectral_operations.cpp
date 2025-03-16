#include "../include/spectral_operations.h"
#include "../include/laplacian_eigen.h"
#include <algorithm>
#include <omp.h>

std::pair<Partition, Partition> bisectGraph(const Partition& graph) {
    int n = graph.vertices.size();
    
    Eigen::MatrixXd laplacian = computeLaplacian(graph.adjacency);
    auto [fiedler_vector, fiedler_value] = computeFiedlerVector(laplacian);
    
    std::vector<int> partition1_idx, partition2_idx;
    for (int i = 0; i < n; ++i) {
        if (fiedler_vector(i) < 0) {
            partition1_idx.push_back(i);
        } else {
            partition2_idx.push_back(i);
        }
    }
    
    std::vector<int> partition1_vertices, partition2_vertices;
    for (int idx : partition1_idx) {
        partition1_vertices.push_back(graph.vertices[idx]);
    }
    for (int idx : partition2_idx) {
        partition2_vertices.push_back(graph.vertices[idx]);
    }
    
    int n1 = partition1_idx.size();
    int n2 = partition2_idx.size();
    
    Eigen::MatrixXd adjacency1 = Eigen::MatrixXd::Zero(n1, n1);
    Eigen::MatrixXd adjacency2 = Eigen::MatrixXd::Zero(n2, n2);
    
    #pragma omp parallel for collapse(2) schedule(dynamic)
    for (int i = 0; i < n1; ++i) {
        for (int j = 0; j < n1; ++j) {
            adjacency1(i, j) = graph.adjacency(partition1_idx[i], partition1_idx[j]);
        }
    }
    
    #pragma omp parallel for collapse(2) schedule(dynamic)
    for (int i = 0; i < n2; ++i) {
        for (int j = 0; j < n2; ++j) {
            adjacency2(i, j) = graph.adjacency(partition2_idx[i], partition2_idx[j]);
        }
    }
    
    Partition p1 = { partition1_vertices, adjacency1 };
    Partition p2 = { partition2_vertices, adjacency2 };
    
    return { p1, p2 };
}

void recursiveSpectralBisection(std::vector<Partition>& partitions, int target_partitions) {
    if (partitions.size() >= target_partitions) {
        return;
    }
    
    auto it = std::max_element(partitions.begin(), partitions.end(), 
                            [](const Partition& a, const Partition& b) {
                                return a.vertices.size() < b.vertices.size();
                            });
    
    if (it->vertices.size() > 1) {
        auto [p1, p2] = bisectGraph(*it);
        *it = p1;
        partitions.push_back(p2);
        recursiveSpectralBisection(partitions, target_partitions);
    }
}

std::vector<Partition> parallelSpectralPartitioning(const Eigen::MatrixXd& adjacency, int num_partitions) {
    int n = adjacency.rows();
    std::vector<int> all_vertices(n);
    for (int i = 0; i < n; ++i) {
        all_vertices[i] = i;
    }
    
    Partition initial_partition = { all_vertices, adjacency };
    std::vector<Partition> partitions = { initial_partition };
    
    while (partitions.size() < num_partitions) {
        int current_size = partitions.size();
        int new_partitions_needed = std::min(current_size, num_partitions - current_size);
        
        std::sort(partitions.begin(), partitions.end(), 
                [](const Partition& a, const Partition& b) {
                    return a.vertices.size() > b.vertices.size();
                });
        
        std::vector<std::pair<Partition, Partition>> new_partitions(new_partitions_needed);
        
        #pragma omp parallel for schedule(dynamic)
        for (int i = 0; i < new_partitions_needed; ++i) {
            if (partitions[i].vertices.size() > 1) {
                new_partitions[i] = bisectGraph(partitions[i]);
            }
        }
        
        for (int i = 0; i < new_partitions_needed; ++i) {
            if (partitions[i].vertices.size() > 1) {
                partitions[i] = new_partitions[i].first;
                partitions.push_back(new_partitions[i].second);
            }
        }
        
        if (current_size == partitions.size()) {
            break;
        }
    }
    
    return partitions;
}
