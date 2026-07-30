from __future__ import annotations

from fractions import Fraction
from math import gcd
from typing import Any

ALLOWED_VARS = {"n1", "d1", "n2", "d2"}
ALLOWED_OPS = {"add", "sub", "mul", "lcm", "fraction"}


class DSLValidationError(ValueError):
    pass


def validate(node: Any, depth: int = 0, counter: list[int] | None = None) -> None:
    if counter is None:
        counter = [0]
    counter[0] += 1
    if counter[0] > 32 or depth > 8:
        raise DSLValidationError("expression is too complex")
    if isinstance(node, int):
        return
    if isinstance(node, dict) and set(node) == {"var"} and node["var"] in ALLOWED_VARS:
        return
    if not isinstance(node, dict) or "op" not in node:
        raise DSLValidationError("invalid node")
    operation = node["op"]
    if operation not in ALLOWED_OPS:
        raise DSLValidationError(f"operator not allowed: {operation}")
    arguments = node.get("args")
    if not isinstance(arguments, list) or len(arguments) != 2:
        raise DSLValidationError("every operator requires exactly two arguments")
    for argument in arguments:
        validate(argument, depth + 1, counter)


def evaluate(node: Any, environment: dict[str, int]) -> int | Fraction:
    validate(node)

    def visit(current: Any) -> int | Fraction:
        if isinstance(current, int):
            return current
        if "var" in current:
            return int(environment[current["var"]])
        left, right = map(visit, current["args"])
        operation = current["op"]
        if operation == "add":
            return left + right
        if operation == "sub":
            return left - right
        if operation == "mul":
            return left * right
        if operation == "lcm":
            left_i, right_i = int(left), int(right)
            divisor = gcd(left_i, right_i)
            return 0 if divisor == 0 else abs(left_i * right_i) // divisor
        if operation == "fraction":
            if right == 0:
                raise DSLValidationError("zero denominator")
            return Fraction(left, right)
        raise DSLValidationError("unreachable")

    return visit(node)
