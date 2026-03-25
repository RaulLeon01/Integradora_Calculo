import sympy as sp

from utils.solver import solve_with_laplace


def extract_rhs(latex_string: str) -> str:
    return latex_string


def test_first_order_case_runs():
    result = solve_with_laplace("y' + 2y = 0", "1", "")
    assert result["solution_latex"]


def test_second_order_case_runs():
    result = solve_with_laplace("y'' + 3y' + 2y = 0", "0", "1")
    assert result["ys_latex"]


def test_trig_case_runs():
    result = solve_with_laplace("y'' + y = sin(t)", "0", "0")
    assert result["transform_latex"]
