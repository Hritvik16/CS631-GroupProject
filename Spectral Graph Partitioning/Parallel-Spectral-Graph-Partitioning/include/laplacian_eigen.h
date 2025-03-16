#ifndef LAPLACIAN_EIGEN_H
#define LAPLACIAN_EIGEN_H

#include <eigen3/Eigen/Dense>
#include <utility>

// Computes the Laplacian matrix from the given adjacency matrix.
Eigen::MatrixXd computeLaplacian(const Eigen::MatrixXd& adjacency);

// Computes the Fiedler vector (the eigenvector corresponding to the second smallest eigenvalue and returns it along with the eigenvalue.
std::pair<Eigen::VectorXd, double> computeFiedlerVector(const Eigen::MatrixXd& laplacian);

#endif // LAPLACIAN_EIGEN_H
