"""JSON persistence for student records."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime

from student import Student

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "students.json")


class StorageError(Exception):
    """Raised when student data cannot be read or written."""


def ensure_data_dir(path: str = DATA_DIR) -> None:
    os.makedirs(path, exist_ok=True)


def load_students(path: str = DATA_FILE) -> list[Student]:
    """Load students from a JSON file, returning an empty list when absent."""
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except json.JSONDecodeError as exc:
        backup = f"{path}.corrupt-{datetime.now():%Y%m%d%H%M%S}"
        try:
            os.replace(path, backup)
        except OSError:
            backup = path
        raise StorageError(
            f"The data file was corrupted and has been moved to {backup}. "
            f"Details: {exc}"
        ) from exc
    except OSError as exc:
        raise StorageError(f"Could not read {path}: {exc}") from exc

    if isinstance(raw, dict):
        entries = raw.get("students", [])
    elif isinstance(raw, list):
        entries = raw
    else:
        raise StorageError("Unexpected data format: expected an object or a list.")

    if not isinstance(entries, list):
        raise StorageError("The 'students' value must be a list.")

    students: list[Student] = []
    for index, entry in enumerate(entries, start=1):
        try:
            students.append(Student.from_dict(entry))
        except (ValueError, TypeError) as exc:
            print(
                f"Warning: skipped invalid student record #{index}: {exc}",
                file=sys.stderr,
            )
    return students


def save_students(students: list[Student], path: str = DATA_FILE) -> None:
    """Save students to JSON atomically, creating directories as needed."""
    directory = os.path.dirname(path)
    if directory:
        ensure_data_dir(directory)
    payload = {
        "school": "Bright Future Secondary School",
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "students": [student.to_dict() for student in students],
    }

    temporary_path = f"{path}.tmp"
    try:
        with open(temporary_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temporary_path, path)
    except OSError as exc:
        raise StorageError(f"Could not save student data to {path}: {exc}") from exc
    finally:
        if os.path.exists(temporary_path):
            try:
                os.remove(temporary_path)
            except OSError:
                pass
