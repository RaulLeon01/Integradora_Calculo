from __future__ import annotations

import base64
import io
import re
from dataclasses import dataclass
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)


t = sp.symbols("t", real=True, nonnegative=True)
s = sp.symbols("s", real=True)
Y = sp.symbols("Y")
y = sp.Function("y")

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


class SolverError(Exception):
    pass


@dataclass
class ParsedEquation:
    order: int
    a2: sp.Expr
    a1: sp.Expr
    a0: sp.Expr
    forcing: sp.Expr
    standardized_equation: sp.Eq


# Local symbols allowed in user input.
LOCAL_DICT = {
    "t": t,
    "e": sp.E,
    "pi": sp.pi,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "exp": sp.exp,
    "sqrt": sp.sqrt,
    "log": sp.log,
}


def solve_with_laplace(equation_text: str, y0_text: str, y1_text: str) -> dict[str, Any]:
    parsed = parse_linear_equation(equation_text)
    y0 = parse_scalar(y0_text, "y(0)")
    y1 = parse_scalar(y1_text, "y'(0)") if parsed.order == 2 else sp.Integer(0)

    transformed_equation, ys_expr, solution_expr = build_laplace_solution(parsed, y0, y1)
    plot_base64 = plot_solution(solution_expr)

    conditions = [sp.Eq(y(0), y0)]
    if parsed.order == 2:
        conditions.append(sp.Eq(sp.diff(y(t), t).subs(t, 0), y1))

    return {
        "order": parsed.order,
        "equation_latex": sp.latex(parsed.standardized_equation),
        "conditions_latex": [sp.latex(cond) for cond in conditions],
        "forcing_latex": sp.latex(sp.Eq(sp.Function("f")(t), parsed.forcing)),
        "transform_latex": sp.latex(transformed_equation),
        "ys_latex": sp.latex(sp.Eq(sp.Function("Y")(s), ys_expr)),
        "solution_latex": sp.latex(sp.Eq(y(t), solution_expr)),
        "plot_base64": plot_base64,
        "ai_context": {
            "equation": sp.latex(parsed.standardized_equation),
            "conditions": [sp.latex(cond) for cond in conditions],
            "transform": sp.latex(transformed_equation),
            "ys": sp.latex(sp.Eq(sp.Function("Y")(s), ys_expr)),
            "solution": sp.latex(sp.Eq(y(t), solution_expr)),
            "forcing": sp.latex(parsed.forcing),
            "order": parsed.order,
        },
    }


def normalize_text(text: str) -> str:
    text = (text or "").strip().lower()
    replacements = {
        "−": "-",
        "–": "-",
        "—": "-",
        "′": "'",
        "’": "'",
        "“": '"',
        "”": '"',
        "·": "*",
    }
    for original, replacement in replacements.items():
        text = text.replace(original, replacement)
    text = re.sub(r"\s+", " ", text)
    return text


def replace_equation_tokens(expr_text: str) -> str:
    expr_text = expr_text.replace("y''", "Y2")
    expr_text = expr_text.replace("y'", "Y1")
    expr_text = expr_text.replace("y", "Y0")
    return expr_text


def parse_user_expression(expr_text: str) -> sp.Expr:
    try:
        expr = parse_expr(
            expr_text,
            local_dict={**LOCAL_DICT, "Y0": sp.Symbol("Y0"), "Y1": sp.Symbol("Y1"), "Y2": sp.Symbol("Y2")},
            transformations=TRANSFORMATIONS,
            evaluate=True,
        )
    except Exception as exc:
        raise SolverError(f"No pude interpretar la expresión: {expr_text}") from exc
    return sp.expand(expr)


def parse_linear_equation(equation_text: str) -> ParsedEquation:
    text = normalize_text(equation_text)
    if "=" not in text:
        raise SolverError("La ecuación debe incluir el signo '='.")

    lhs_text, rhs_text = [part.strip() for part in text.split("=", 1)]
    lhs_expr = parse_user_expression(replace_equation_tokens(lhs_text))
    rhs_expr = parse_user_expression(replace_equation_tokens(rhs_text))

    equation_expr = sp.expand(lhs_expr - rhs_expr)
    Y2, Y1, Y0 = sp.symbols("Y2 Y1 Y0")

    try:
        poly = sp.Poly(equation_expr, Y2, Y1, Y0)
    except Exception as exc:
        raise SolverError(
            "La ecuación debe ser lineal y estar escrita con y'', y' y y."
        ) from exc

    for monomial in poly.monoms():
        if sum(monomial) > 1:
            raise SolverError(
                "Solo se admiten ecuaciones diferenciales lineales de primer o segundo orden."
            )

    a2 = sp.simplify(poly.coeff_monomial(Y2))
    a1 = sp.simplify(poly.coeff_monomial(Y1))
    a0 = sp.simplify(poly.coeff_monomial(Y0))
    constant_term = sp.simplify(poly.coeff_monomial(1))
    forcing = sp.simplify(-constant_term)

    coefficients = [a2, a1, a0]
    for coefficient in coefficients:
        if t in coefficient.free_symbols:
            raise SolverError(
                "Por ahora solo se admiten coeficientes constantes en y'', y' y y."
            )

    if a2 != 0:
        order = 2
    elif a1 != 0:
        order = 1
    else:
        raise SolverError(
            "No detecté una derivada válida. Usa y' o y'' en la ecuación."
        )

    standardized_equation = sp.Eq(
        sp.simplify(a2 * sp.diff(y(t), (t, 2)) + a1 * sp.diff(y(t), t) + a0 * y(t)),
        sp.simplify(forcing),
    )

    return ParsedEquation(
        order=order,
        a2=a2,
        a1=a1,
        a0=a0,
        forcing=forcing,
        standardized_equation=standardized_equation,
    )


def parse_scalar(value_text: str, field_name: str) -> sp.Expr:
    value_text = normalize_text(value_text)
    if not value_text:
        raise SolverError(f"Debes capturar la condición inicial {field_name}.")

    try:
        value = parse_expr(
            value_text,
            local_dict=LOCAL_DICT,
            transformations=TRANSFORMATIONS,
            evaluate=True,
        )
    except Exception as exc:
        raise SolverError(f"No pude interpretar el valor de {field_name}.") from exc

    if t in value.free_symbols:
        raise SolverError(f"{field_name} debe ser una constante, no una función de t.")
    return sp.simplify(value)


def build_laplace_solution(parsed: ParsedEquation, y0: sp.Expr, y1: sp.Expr) -> tuple[sp.Eq, sp.Expr, sp.Expr]:
    Gs = sp.laplace_transform(parsed.forcing, t, s, noconds=True)

    if parsed.order == 1:
        transformed_eq = sp.Eq(parsed.a1 * (s * Y - y0) + parsed.a0 * Y, Gs)
    else:
        transformed_eq = sp.Eq(
            parsed.a2 * (s**2 * Y - s * y0 - y1)
            + parsed.a1 * (s * Y - y0)
            + parsed.a0 * Y,
            Gs,
        )

    ys_expr = sp.solve(transformed_eq, Y)
    if not ys_expr:
        raise SolverError("No se pudo despejar Y(s).")
    ys_expr = sp.simplify(ys_expr[0])

    try:
        ys_for_inverse = sp.apart(ys_expr, s)
    except Exception:
        ys_for_inverse = ys_expr

    solution_expr = sp.simplify(sp.inverse_laplace_transform(ys_for_inverse, s, t))
    solution_expr = solution_expr.subs(sp.Heaviside(t), 1)
    solution_expr = sp.simplify(solution_expr)

    transformed_display = transformed_eq.subs(Y, sp.Function("Y")(s))
    return transformed_display, ys_expr, solution_expr


def plot_solution(solution_expr: sp.Expr) -> str:
    figure, axis = plt.subplots(figsize=(8, 4.2), dpi=140)
    xs = np.linspace(0.0, 10.0, 500)

    try:
        numeric_function = sp.lambdify(t, solution_expr, modules=["numpy"])
        ys = np.array(numeric_function(xs), dtype=np.complex128)
        if np.max(np.abs(ys.imag)) < 1e-9:
            ys = ys.real
        else:
            ys = np.real_if_close(ys)
    except Exception:
        ys = np.zeros_like(xs)

    axis.plot(xs, ys, linewidth=2.5)
    axis.set_title("Gráfica de la solución y(t)")
    axis.set_xlabel("t")
    axis.set_ylabel("y(t)")
    axis.grid(True, alpha=0.35)

    buffer = io.BytesIO()
    figure.tight_layout()
    figure.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(figure)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")
