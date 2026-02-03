"""Live-coded demo: solving a discretized quantum equation."""
from __future__ import annotations

import math
from typing import List, Tuple


def show_line(line_no: int, text: str) -> None:
    print(f"{line_no:02d}: {text}")


def build_hamiltonian(n_points: int, length: float) -> Tuple[List[List[float]], float]:
    dx = length / (n_points + 1)
    coeff = 1.0 / (dx * dx)
    size = n_points
    matrix = [[0.0 for _ in range(size)] for _ in range(size)]
    for i in range(size):
        matrix[i][i] = 2.0 * coeff
        if i > 0:
            matrix[i][i - 1] = -coeff
        if i < size - 1:
            matrix[i][i + 1] = -coeff
    return matrix, dx


def max_offdiag(a: List[List[float]]) -> Tuple[int, int, float]:
    size = len(a)
    max_val = 0.0
    p = 0
    q = 1
    for i in range(size):
        for j in range(i + 1, size):
            val = abs(a[i][j])
            if val > max_val:
                max_val = val
                p, q = i, j
    return p, q, max_val


def jacobi_eigenvalues(a: List[List[float]], eps: float = 1e-10, max_iter: int = 200) -> List[float]:
    size = len(a)
    for _ in range(max_iter):
        p, q, off = max_offdiag(a)
        if off < eps:
            break
        if a[p][p] == a[q][q]:
            angle = math.pi / 4
        else:
            angle = 0.5 * math.atan2(2 * a[p][q], a[q][q] - a[p][p])
        c = math.cos(angle)
        s = math.sin(angle)

        app = c * c * a[p][p] - 2 * s * c * a[p][q] + s * s * a[q][q]
        aqq = s * s * a[p][p] + 2 * s * c * a[p][q] + c * c * a[q][q]
        a[p][p] = app
        a[q][q] = aqq
        a[p][q] = 0.0
        a[q][p] = 0.0

        for i in range(size):
            if i in (p, q):
                continue
            aip = c * a[i][p] - s * a[i][q]
            aiq = s * a[i][p] + c * a[i][q]
            a[i][p] = aip
            a[p][i] = aip
            a[i][q] = aiq
            a[q][i] = aiq
    return sorted(a[i][i] for i in range(size))


def main() -> None:
    line = 1
    show_line(line, "hbar = 1.0")
    hbar = 1.0
    line += 1
    show_line(line, "mass = 1.0")
    mass = 1.0
    line += 1
    show_line(line, "length = 1.0")
    length = 1.0
    line += 1
    show_line(line, "n_points = 30")
    n_points = 30
    line += 1
    show_line(line, "hamiltonian, dx = build_hamiltonian(n_points, length)")
    hamiltonian, dx = build_hamiltonian(n_points, length)
    line += 1
    show_line(line, "scale = -(hbar ** 2) / (2 * mass)")
    scale = -(hbar ** 2) / (2 * mass)
    line += 1
    show_line(line, "for i in range(n_points): hamiltonian[i][i] *= -scale")
    for i in range(n_points):
        hamiltonian[i][i] *= -scale
    line += 1
    show_line(line, "for i in range(n_points - 1): hamiltonian[i][i + 1] *= -scale")
    for i in range(n_points - 1):
        hamiltonian[i][i + 1] *= -scale
        hamiltonian[i + 1][i] *= -scale
    line += 1
    show_line(line, "eigenvalues = jacobi_eigenvalues(hamiltonian)")
    eigenvalues = jacobi_eigenvalues(hamiltonian)
    line += 1
    show_line(line, "ground_energy = eigenvalues[0]")
    ground_energy = eigenvalues[0]
    line += 1
    show_line(line, "print(ground_energy)")
    print(f"\nComputed dx={dx:.4f}, ground state energy ≈ {ground_energy:.6f}")


if __name__ == "__main__":
    main()
