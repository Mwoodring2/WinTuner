"""Local change log for applied tweaks (JSON-backed)."""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_LOG_DIR = Path.home() / ".wintuner"
_DEFAULT_LOG_FILE = _DEFAULT_LOG_DIR / "change_log.json"


@dataclass
class ChangeRecord:
    """A single logged change made by WinTuner."""

    record_id: str
    timestamp: str
    tweak_id: str
    tweak_title: str
    previous_value: Any
    new_value: Any
    success: bool
    error_message: str = ""
    undo_available: bool = True
    undone: bool = False

    @classmethod
    def create(
        cls,
        tweak_id: str,
        tweak_title: str,
        previous_value: Any,
        new_value: Any,
        success: bool,
        error_message: str = "",
        undo_available: bool = True,
    ) -> ChangeRecord:
        """Factory for a new change record with auto-generated id and timestamp."""
        return cls(
            record_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            tweak_id=tweak_id,
            tweak_title=tweak_title,
            previous_value=previous_value,
            new_value=new_value,
            success=success,
            error_message=error_message,
            undo_available=undo_available,
        )

    def validate(self) -> list[str]:
        """Return validation errors."""
        errors: list[str] = []
        if not self.record_id:
            errors.append("Missing record_id")
        if not self.tweak_id:
            errors.append("Missing tweak_id")
        if not self.timestamp:
            errors.append("Missing timestamp")
        return errors


class ChangeLog:
    """Persistent JSON change log."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or _DEFAULT_LOG_FILE
        self._records: list[ChangeRecord] = []
        self._load()

    @property
    def path(self) -> Path:
        return self._path

    def _load(self) -> None:
        if not self._path.exists():
            self._records = []
            return
        try:
            with open(self._path, encoding="utf-8") as fh:
                raw = json.load(fh)
            self._records = [ChangeRecord(**item) for item in raw.get("records", [])]
        except (json.JSONDecodeError, OSError, TypeError) as exc:
            logger.error("Failed to load change log: %s", exc)
            self._records = []

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {"records": [asdict(r) for r in self._records]}
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, default=str)

    def add(self, record: ChangeRecord) -> None:
        """Append a change record and persist."""
        self._records.insert(0, record)
        self._save()

    def get_all(self) -> list[ChangeRecord]:
        """Return all records, newest first."""
        return list(self._records)

    def get_undoable(self) -> list[ChangeRecord]:
        """Return successful, non-undone records that support undo."""
        return [
            r
            for r in self._records
            if r.success and r.undo_available and not r.undone
        ]

    def get_recent(self, limit: int = 10) -> list[ChangeRecord]:
        """Return the most recent records."""
        return self._records[:limit]

    def mark_undone(self, record_id: str) -> bool:
        """Mark a record as undone. Returns True if found."""
        for record in self._records:
            if record.record_id == record_id:
                record.undone = True
                self._save()
                return True
        return False

    def find_by_id(self, record_id: str) -> ChangeRecord | None:
        """Find a record by id."""
        for record in self._records:
            if record.record_id == record_id:
                return record
        return None
