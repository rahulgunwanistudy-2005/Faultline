#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from collections import deque
from importlib import metadata
from pathlib import Path

try:
    from packaging.markers import default_environment
    from packaging.requirements import Requirement
    from packaging.utils import canonicalize_name
    from packaging.version import Version
except ImportError:  # packaging is vendored with pip in minimal virtual environments
    from pip._vendor.packaging.markers import default_environment
    from pip._vendor.packaging.requirements import Requirement
    from pip._vendor.packaging.utils import canonicalize_name
    from pip._vendor.packaging.version import Version

ROOT = Path(__file__).resolve().parents[1]
PIN = re.compile(r"^([A-Za-z0-9_.-]+)==([^;\s]+)$")


def declared_pins() -> dict[str, str]:
    pins: dict[str, str] = {}
    for path in (ROOT / "apps/api/requirements.txt", ROOT / "requirements-dev.txt"):
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or line.startswith("-r "):
                continue
            match = PIN.fullmatch(line)
            if not match:
                raise RuntimeError(f"Dependency is not exactly pinned: {path.name}: {line}")
            name, version = match.groups()
            pins[canonicalize_name(name)] = version
    return pins


def main() -> int:
    pins = declared_pins()
    failures: list[str] = []
    queue: deque[str] = deque(pins)
    checked: set[str] = set()
    environment = default_environment()

    for name, expected in pins.items():
        try:
            installed = metadata.version(name)
        except metadata.PackageNotFoundError:
            failures.append(f"missing direct dependency: {name}=={expected}")
            continue
        if Version(installed) != Version(expected):
            failures.append(f"direct dependency mismatch: {name} expected {expected}, found {installed}")

    while queue:
        name = canonicalize_name(queue.popleft())
        if name in checked:
            continue
        checked.add(name)
        try:
            distribution = metadata.distribution(name)
        except metadata.PackageNotFoundError:
            continue
        for raw_requirement in distribution.requires or ():
            requirement = Requirement(raw_requirement)
            marker_environment = dict(environment)
            marker_environment["extra"] = ""
            if requirement.marker and not requirement.marker.evaluate(marker_environment):
                continue
            dependency = canonicalize_name(requirement.name)
            try:
                installed = metadata.version(dependency)
            except metadata.PackageNotFoundError:
                failures.append(f"{name} requires missing dependency {requirement}")
                continue
            if requirement.specifier and Version(installed) not in requirement.specifier:
                failures.append(
                    f"{name} requires {requirement.specifier} for {dependency}, found {installed}"
                )
            queue.append(dependency)

    if failures:
        print("Project dependency closure is inconsistent:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    rendered = ", ".join(f"{name}=={version}" for name, version in sorted(pins.items()))
    print(f"Direct pins match and the project dependency closure is consistent: {rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
