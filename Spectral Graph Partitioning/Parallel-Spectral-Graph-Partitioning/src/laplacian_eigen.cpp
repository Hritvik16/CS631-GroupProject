#include "../include/laplacian_eigen.h"
#include <iostream>
#include <cstdlib>
#include <eigen3/Eigen/Eigenvalues>

Eigen::MatrixXd computeLaplacian(const Eigen::MatrixXd& adjacency) {
    int n = adjacency.rows();
    Eigen::VectorXd degrees = adjacency.rowwise().sum();
    Eigen::MatrixXd degree_matrix = Eigen::MatrixXd::Zero(n, n);
    
    for (int i = 0; i < n; ++i) {
        degree_matrix(i, i) = degrees(i);
    }
    
    return degree_matrix - adjacency;
}

std::pair<Eigen::VectorXd, double> computeFiedlerVector(const Eigen::MatrixXd& laplacian) {
    Eigen::SelfAdjointEigenSolver<Eigen::MatrixXd> eigensolver(laplacian);
    
    if (eigensolver.info() != Eigen::Success) {
        std::cerr << "Eigenvalue decomposition failed!" << std::endl;
        exit(1);
    }
    
    Eigen::VectorXd eigenvalues = eigensolver.eigenvalues();
    Eigen::MatrixXd eigenvectors = eigensolver.eigenvectors();
    
    double fiedler_value = eigenvalues(1);
    Eigen::VectorXd fiedler_vector = eigenvectors.col(1);
    
    return {fiedler_vector, fiedler_value};
}
