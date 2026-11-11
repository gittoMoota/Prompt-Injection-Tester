"""Loads attack cases from YAML files."""

from __future__ import annotations

from pathlib import Path

import yaml

from promptprobe.models import AttackCase, Category, Severity

DEFAULT_PAYLOAD_DIR = Path(__file__).parent / "payloads"
_SEVERITY_RANK = {severity: rank for rank, severity in enumerate(Severity)}


class AttackLibraryError(Exception):
    """Raised when an attack file is missing or malformed."""


class AttackLibrary:
    def __init__(self, attacks: list[AttackCase]) -> None:
        self._attacks = list(attacks)

    def __len__(self) -> int:
        return len(self._attacks)

    @classmethod
    def from_directory(
        cls, directory: Path | str = DEFAULT_PAYLOAD_DIR
    ) -> AttackLibrary:
        directory = Path(directory)
        if not directory.is_dir():
            raise AttackLibraryError(f"Payload directory not found: {directory}")
        attacks: list[AttackCase] = []
        for path in sorted(directory.glob("*.yaml")):
            attacks.extend(_load_file(path))
        _check_unique_ids(attacks)
        return cls(attacks)

    def all(self) -> list[AttackCase]:
        return list(self._attacks)

    def filter(
        self,
        category: Category | None = None,
        min_severity: Severity | None = None,
    ) -> list[AttackCase]:
        selected = self._attacks
        if category is not None:
            selected = [a for a in selected if a.category == category]
        if min_severity is not None:
            floor = _SEVERITY_RANK[min_severity]
            selected = [a for a in selected if _SEVERITY_RANK[a.severity] >= floor]
        return list(selected)


def _load_file(path: Path) -> list[AttackCase]:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise AttackLibraryError(f"Invalid YAML in {path.name}: {exc}") from exc
    if not isinstance(raw, list):
        raise AttackLibraryError(f"{path.name} must contain a list of attacks")
    return [_to_attack(item, path.name) for item in raw]


def _to_attack(item: object, filename: str) -> AttackCase:
    if not isinstance(item, dict):
        raise AttackLibraryError(f"{filename}: each attack must be a mapping")
    try:
        return AttackCase(
            id=str(item["id"]),
            category=Category(item["category"]),
            severity=Severity(item["severity"]),
            prompt=str(item["prompt"]),
            description=str(item.get("description", "")),
        )
    except KeyError as exc:
        raise AttackLibraryError(f"{filename}: missing field {exc}") from exc
    except ValueError as exc:
        raise AttackLibraryError(f"{filename}: {exc}") from exc


def _check_unique_ids(attacks: list[AttackCase]) -> None:
    seen: set[str] = set()
    for attack in attacks:
        if attack.id in seen:
            raise AttackLibraryError(f"Duplicate attack id: {attack.id}")
        seen.add(attack.id)