"""SQLite implementation of the C03 application persistence boundary."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Sequence, TypeVar

from pydantic import BaseModel

from strategic_intelligence.domain.models import (
    Case, Claim, ClaimEvidenceLink, Evidence, Source, WorkflowRun, WorkflowStage,
)

T = TypeVar("T", bound=BaseModel)


class CheckpointRejectedError(ValueError):
    """Raised when a checkpoint's required persisted records are absent."""


_SCHEMA_VERSION = "001_initial"
_SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS workflow_runs (id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sources (id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), url TEXT NOT NULL, payload TEXT NOT NULL, UNIQUE(case_id, url));
CREATE TABLE IF NOT EXISTS evidence (id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), source_id TEXT NOT NULL REFERENCES sources(id), content TEXT NOT NULL, payload TEXT NOT NULL, UNIQUE(case_id, source_id, content));
CREATE TABLE IF NOT EXISTS claims (id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), text TEXT NOT NULL, payload TEXT NOT NULL, UNIQUE(case_id, text));
CREATE TABLE IF NOT EXISTS claim_evidence_links (claim_id TEXT NOT NULL REFERENCES claims(id), evidence_id TEXT NOT NULL REFERENCES evidence(id), relationship_type TEXT NOT NULL, PRIMARY KEY(claim_id, evidence_id, relationship_type));
CREATE TABLE IF NOT EXISTS checkpoints (run_id TEXT NOT NULL REFERENCES workflow_runs(id), stage TEXT NOT NULL, accepted INTEGER NOT NULL, required_records TEXT NOT NULL, accepted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(run_id, stage));
"""


class SqliteRepository:
    """Small V1 repository; domain/application code never issues SQLite queries."""

    def __init__(self, database_path: Path) -> None:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(database_path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._initialize_schema()

    def close(self) -> None:
        self._connection.close()

    def create_case(self, case: Case) -> Case:
        with self._connection:
            self._connection.execute("INSERT INTO cases(id, payload) VALUES (?, ?)", (case.case_id, self._dump(case)))
        return case

    def get_case(self, case_id: str) -> Case | None:
        row = self._connection.execute("SELECT payload FROM cases WHERE id = ?", (case_id,)).fetchone()
        return None if row is None else self._load(Case, row["payload"])

    def update_case(self, case: Case) -> Case:
        with self._connection:
            result = self._connection.execute("UPDATE cases SET payload = ? WHERE id = ?", (self._dump(case), case.case_id))
            if result.rowcount != 1:
                raise KeyError(f"case not found: {case.case_id}")
        return case

    def save_workflow_run(self, run: WorkflowRun) -> WorkflowRun:
        return self._upsert("workflow_runs", run.run_id, run.case_id, self._dump(run))

    def get_workflow_run(self, run_id: str) -> WorkflowRun | None:
        return self._get("workflow_runs", WorkflowRun, run_id)

    def save_source(self, source: Source) -> Source:
        row = self._connection.execute("SELECT payload FROM sources WHERE case_id = ? AND url = ?", (source.case_id, source.url)).fetchone()
        if row:
            return self._load(Source, row["payload"])
        with self._connection:
            self._connection.execute("INSERT INTO sources(id, case_id, url, payload) VALUES (?, ?, ?, ?)", (source.source_id, source.case_id, source.url, self._dump(source)))
        return source

    def get_source(self, source_id: str) -> Source | None:
        return self._get("sources", Source, source_id)

    def save_evidence(self, evidence: Evidence) -> Evidence:
        row = self._connection.execute("SELECT payload FROM evidence WHERE case_id = ? AND source_id = ? AND content = ?", (evidence.case_id, evidence.source_id, evidence.content)).fetchone()
        if row:
            return self._load(Evidence, row["payload"])
        with self._connection:
            self._connection.execute("INSERT INTO evidence(id, case_id, source_id, content, payload) VALUES (?, ?, ?, ?, ?)", (evidence.evidence_id, evidence.case_id, evidence.source_id, evidence.content, self._dump(evidence)))
        return evidence

    def get_evidence(self, evidence_id: str) -> Evidence | None:
        return self._get("evidence", Evidence, evidence_id)

    def save_claim_with_links(self, claim: Claim, links: Sequence[ClaimEvidenceLink]) -> Claim:
        if {link.claim_id for link in links} != {claim.claim_id} or {link.evidence_id for link in links} != set(claim.evidence_ids):
            raise ValueError("claim links must exactly match claim evidence identifiers")
        with self._connection:
            self._connection.execute("INSERT INTO claims(id, case_id, text, payload) VALUES (?, ?, ?, ?)", (claim.claim_id, claim.case_id, claim.text, self._dump(claim)))
            for link in links:
                self._connection.execute("INSERT INTO claim_evidence_links(claim_id, evidence_id, relationship_type) VALUES (?, ?, ?)", (link.claim_id, link.evidence_id, link.relationship_type.value))
        return claim

    def get_claim(self, claim_id: str) -> Claim | None:
        return self._get("claims", Claim, claim_id)

    def accept_checkpoint(self, run_id: str, stage: WorkflowStage, required_records: Sequence[tuple[str, str]]) -> None:
        tables = {"case": "cases", "source": "sources", "evidence": "evidence", "claim": "claims", "workflow_run": "workflow_runs"}
        with self._connection:
            for kind, record_id in required_records:
                table = tables.get(kind)
                if table is None or self._connection.execute(f"SELECT 1 FROM {table} WHERE id = ?", (record_id,)).fetchone() is None:
                    raise CheckpointRejectedError(f"required persisted record is missing: {kind}/{record_id}")
            self._connection.execute("INSERT OR REPLACE INTO checkpoints(run_id, stage, accepted, required_records) VALUES (?, ?, 1, ?)", (run_id, stage.value, json.dumps(required_records)))

    def checkpoint_is_accepted(self, run_id: str, stage: WorkflowStage) -> bool:
        row = self._connection.execute("SELECT accepted FROM checkpoints WHERE run_id = ? AND stage = ?", (run_id, stage.value)).fetchone()
        return bool(row and row["accepted"])

    def link_count(self, claim_id: str) -> int:
        return self._connection.execute("SELECT COUNT(*) FROM claim_evidence_links WHERE claim_id = ?", (claim_id,)).fetchone()[0]

    def _initialize_schema(self) -> None:
        with self._connection:
            self._connection.executescript(_SCHEMA)
            self._connection.execute("INSERT OR IGNORE INTO schema_migrations(version) VALUES (?)", (_SCHEMA_VERSION,))

    def _upsert(self, table: str, identifier: str, case_id: str, payload: str) -> WorkflowRun:
        with self._connection:
            self._connection.execute(f"INSERT INTO {table}(id, case_id, payload) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload", (identifier, case_id, payload))
        return self._load(WorkflowRun, payload)

    def _get(self, table: str, model_type: type[T], identifier: str) -> T | None:
        row = self._connection.execute(f"SELECT payload FROM {table} WHERE id = ?", (identifier,)).fetchone()
        return None if row is None else self._load(model_type, row["payload"])

    @staticmethod
    def _dump(model: BaseModel) -> str:
        return model.model_dump_json()

    @staticmethod
    def _load(model_type: type[T], payload: str) -> T:
        return model_type.model_validate_json(payload)
