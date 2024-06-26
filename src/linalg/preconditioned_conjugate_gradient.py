import numpy as np


def pcg(A, b, maxiter=None, rtol=1e-6, atol=1e-6, P=None):
    """
    Preconditioned Conjugate Gradient (PCG) method for solving a linear system Ax = b.

    Parameters
    ----------
    A : np.ndarray
        The matrix representing the linear system, of size (n, n).
    b : np.ndarray
        The right-hand side vector of the linear system, of size (n,).
    maxiter : int, optional
        The maximum number of iterations allowed. Default is 10 * n.
    rtol : float, optional
        The relative tolerance for convergence. Default is 1e-6.
    atol : float, optional
        The absolute tolerance for convergence. Default is 1e-6.
    P : np.ndarray, optional
        The preconditioner matrix, of size (n, p). If None, the identity matrix is used. Default is None.

    Returns
    -------
    x : np.ndarray
        The approximate solution to the linear system, of size (n,).
    C : np.ndarray
        The approximation of the inverse of A, of size (n, n).

    Notes
    -----
    - The function uses the matrix inversion lemma to compute the preconditioner inverse.
    - The PCG method is useful for solving large, sparse, symmetric positive-definite systems efficiently.
    - This implementation assumes the preconditioner P is used to improve convergence.

    Example
    -------
    ```
    n = 5  # Example size of the matrix
    A = np.random.randn(n, n)
    A = A.T @ A  # Make A symmetric positive-definite
    b = np.random.randn(n)
    P = np.random.randn(n, 3)  # Example preconditioner with rank 3

    x, C = pcg(A, b, P=P)
    print("Solution:", x)
    print("Inverse Approximation:", C)
    ```
    """

    n = len(b)
    if maxiter is None:
        maxiter = 10 * n

    if P is None:
        P = np.eye(n)

    # compute inverse using matrix inversion lemma
    invP = mat_inv_lemma(A=np.eye(n) * 0.1**2,
                         U=P,
                         C=np.eye(np.shape(P)[1]),
                         V=P)

    x = np.zeros(n)  # initial solution guess
    C = np.zeros_like(A)  # inverse approximation
    r = b - A @ x  # initial residual
    i = 0  # iteration counter
    tol = max(rtol * np.linalg.norm(b), atol)  # threshold
    while np.linalg.norm(r) > tol:  # CG loop
        r = b - A @ x  # residual
        s = invP @ r  # action (NEW)
        alpha = s.T @ r  # observation
        d = (np.eye(n) - C @ A) @ s  # search direction
        eta = s.T @ (A @ d)  # normalization constant
        C += 1.0 / eta * np.outer(d, d)  # inverse estimate
        x += alpha / eta * d  # solution estimate
        i += 1  # update iteration counter
        if i == maxiter:  # convergence criteria
            # raise RuntimeError("No convergence.")   # no convergence
            return x, C

    return x, C


def mat_inv_lemma(A, U, C, V):
    """
    Compute the inverse of a matrix using the matrix inversion lemma (Woodbury matrix identity).

    The matrix inversion lemma is used to compute the inverse of a matrix of the form:
    (A + UCV^T)^-1.

    Parameters
    ----------
    A (np.ndarray): A square matrix of size (n, n).
    U (np.ndarray): A matrix of size (n, k).
    C (np.ndarray): A square matrix of size (k, k).
    V (np.ndarray): A matrix of size (n, k).

    Returns
    -------
    np.ndarray: The inverse of the matrix (A + UCV^T).

    Notes
    -----
    The matrix inversion lemma states that:
    (A + UCV^T)^-1 = A^-1 - A^-1 * U * (C^-1 + V^T * A^-1 * U)^-1 * V^T * A^-1.

    """

    invA = np.linalg.inv(A)
    invC = np.linalg.inv(C)

    a = invA @ U
    b = np.linalg.inv(invC + V.T @ (invA @ U))
    c = V.T @ invA

    inv_mat = invA - a @ (b @ c)

    return inv_mat


if __name__ == "__main__":
    np.random.seed(42)
    N = 3
    A_ = np.random.rand(N, N)
    A_ = A_ @ A_.T
    b_ = np.random.rand(N)

    xsol1 = pcg(A_, b_)
    xsol2, invA_ = pcg(A_, b_)

    print(np.linalg.norm(xsol1 - np.linalg.solve(A_, b_)))
