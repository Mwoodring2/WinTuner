"""Tests for change log persistence."""

from __future__ import annotations

from pathlib import Path

from wintuner.app.core.change_log import ChangeLog, ChangeRecord


def test_change_record_create_and_validate() -> None:
    record = ChangeRecord.create(
        tweak_id="explorer_show_extensions",
        tweak_title="Show File Extensions",
        previous_value=1,
        new_value=0,
        success=True,
    )
    assert record.validate() == []
    assert record.tweak_id == "explorer_show_extensions"
    assert not record.undone


def test_change_log_write_read(tmp_path: Path) -> None:
    log_path = tmp_path / "change_log.json"
    log = ChangeLog(log_path)
    record = ChangeRecord.create(
        tweak_id="test",
        tweak_title="Test Tweak",
        previous_value="a",
        new_value="b",
        success=True,
    )
    log.add(record)
    log2 = ChangeLog(log_path)
    records = log2.get_all()
    assert len(records) == 1
    assert records[0].tweak_id == "test"


def test_undoable_records(tmp_path: Path) -> None:
    log_path = tmp_path / "log.json"
    log = ChangeLog(log_path)
    r1 = ChangeRecord.create("t1", "T1", 0, 1, True, undo_available=True)
    r2 = ChangeRecord.create("t2", "T2", 0, 1, False, undo_available=True)
    log.add(r1)
    log.add(r2)
    undoable = log.get_undoable()
    assert len(undoable) == 1
    assert undoable[0].tweak_id == "t1"


def test_mark_undone(tmp_path: Path) -> None:
    log_path = tmp_path / "log.json"
    log = ChangeLog(log_path)
    record = ChangeRecord.create("t1", "T1", 0, 1, True)
    log.add(record)
    assert log.mark_undone(record.record_id)
    assert log.get_undoable() == []
