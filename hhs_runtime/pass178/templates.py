from __future__ import annotations

from .exact import ExactRational
from .quantum import ComplexExact, QuantumState, double_slit_hamiltonian_nucleus


def relativistic_lab_template() -> dict:
    return {
        "schema": "HHS_PASS_178_RELATIVISTIC_LAB_TEMPLATE_V1",
        "model_kind": "RELATIVISTIC_FREE_PARTICLE",
        "source": "c^2*d_tau^2 == c^2*d_t^2-d_x^2-d_y^2-d_z^2\nE^2-p^2*c^2 == m^2*c^4\n",
        "initial_state": {
            "particle_id": "particle:1",
            "mass": "1",
            "charge": "1",
            "position4": ["0", "0", "0", "0"],
            "four_velocity": ["5/4", "3/4", "0", "0"],
            "proper_step": "1/16",
        },
        "classification": "STANDARD_PHYSICS_EQUATION_WITH_HHS_ADMISSION",
        "terminal_lab": False,
    }


def quantum_lab_template() -> dict:
    H = double_slit_hamiltonian_nucleus()
    return {
        "schema": "HHS_PASS_178_QUANTUM_LAB_TEMPLATE_V1",
        "model_kind": "QUANTUM_FINITE_CAYLEY_STEP",
        "source": "(I+i*dt*H/(2*hbar))*psi_next == (I-i*dt*H/(2*hbar))*psi\n",
        "parameters": {
            "hamiltonian": [
                [[cell.real.num, cell.real.den], [cell.imag.num, cell.imag.den]]
                for row in H for cell in row
            ],
            "matrix_dimension": 3,
            "dt": "1/8",
            "hbar": "1",
        },
        "initial_state": {
            "state_id": "wave:1",
            "step_index": 0,
            "amplitudes": [
                [[1, 1], [0, 1]],
                [[0, 1], [0, 1]],
                [[0, 1], [0, 1]],
            ],
        },
        "classification": "STANDARD_QUANTUM_CAYLEY_NUCLEUS_NOT_DOUBLE_SLIT_TERMINAL",
        "terminal_lab": False,
    }


def harmonicode_lab_template() -> dict:
    return {
        "schema": "HHS_PASS_178_HARMONICODE_LAB_TEMPLATE_V1",
        "model_kind": "HARMONICODE_CONSTRAINT_MEMBRANE",
        "source": "P^4 == A*B\nDelta == P^2-p*q\nA == B == P^2\nu^72 == 1\nO != Pi\n",
        "initial_state": {"P": "2", "A": "4", "B": "4", "p": "1", "q": "1"},
        "classification": "HHS_ADMISSIBILITY_CONSTRAINT",
        "terminal_lab": False,
    }
