"""Local, path-safe artifact adapter."""

from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from strategic_intelligence.application.persistence import ArtifactReference


class ArtifactNotFoundError(FileNotFoundError):
    """Raised when an application-owned artifact reference does not exist."""


class LocalArtifactStore:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def write(self, case_id: str, run_id: str, content: bytes, suffix: str = ".bin") -> ArtifactReference:
        self._validate_identifier(case_id)
        self._validate_identifier(run_id)
        if not suffix.startswith(".") or "/" in suffix or "\\" in suffix:
            raise ValueError("artifact suffix must be a simple extension")
        reference = ArtifactReference(case_id, run_id, str(uuid4()), suffix)
        path = self._path(reference)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return reference

    def read(self, reference: ArtifactReference) -> bytes:
        path = self._path(reference)
        if not path.is_file():
            raise ArtifactNotFoundError(f"artifact not found: {reference.artifact_id}")
        return path.read_bytes()

    def delete_case(self, case_id: str) -> None:
        self._validate_identifier(case_id)
        path = self._contained(self._root / "cases" / case_id)
        if path.exists():
            shutil.rmtree(path)

    def _path(self, reference: ArtifactReference) -> Path:
        self._validate_identifier(reference.case_id)
        self._validate_identifier(reference.run_id)
        self._validate_identifier(reference.artifact_id)
        return self._contained(
            self._root / "cases" / reference.case_id / "runs" / reference.run_id / "artifacts"
            / f"{reference.artifact_id}{reference.suffix}"
        )

    def _contained(self, candidate: Path) -> Path:
        resolved = candidate.resolve()
        if self._root != resolved and self._root not in resolved.parents:
            raise ValueError("artifact path escapes configured storage root")
        return resolved

    @staticmethod
    def _validate_identifier(value: str) -> None:
        if not value or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for char in value):
            raise ValueError("artifact identifiers must be generated safe identifiers")
