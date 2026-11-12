"""Student model and input validation helpers for the result management system."""

from __future__ import annotations

import re
from datetime import date, datetime

ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9/_-]{2,19}$")
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z' .-]{1,49}$")
FORM_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 /-]{0,14}$")

GENDERS = ("Male", "Female", "Other")


def validate_student_id(value: str) -> str:
    """Return a clean student ID or raise ValueError."""
    cleaned = str(value).strip()
    if not ID_PATTERN.fullmatch(cleaned):
        raise ValueError(
            "Student ID must be 3-20 characters and may contain letters, "
            "digits, '/', '_' or '-' (e.g. STU/2026/001)."
        )
    return cleaned


def validate_name(value: str) -> str:
    """Return a tidy full name or raise ValueError."""
    cleaned = " ".join(str(value).split())
    if not NAME_PATTERN.fullmatch(cleaned):
        raise ValueError(
            "Full name must be 2-50 characters using letters, spaces, "
            "apostrophes, hyphens or periods."
        )
    return cleaned


def validate_form(value: str) -> str:
    """Return a tidy class/form label or raise ValueError."""
    cleaned = " ".join(str(value).split()).upper()
    if not FORM_PATTERN.fullmatch(cleaned):
        raise ValueError(
            "Class/Form must be 1-15 characters using letters, digits, "
            "spaces, '/' or '-' (e.g. SS1, JSS 2, FORM A)."
        )
    return cleaned


def validate_gender(value: str) -> str:
    """Return a supported gender value or raise ValueError."""
    cleaned = str(value).strip().title()
    for gender in GENDERS:
        if cleaned.lower() == gender.lower():
            return gender
    raise ValueError("Gender must be Male, Female or Other.")


def validate_date_of_birth(value: str) -> str:
    """Return an ISO date string (YYYY-MM-DD) or raise ValueError."""
    cleaned = str(value).strip()
    try:
        parsed = datetime.strptime(cleaned, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("Date of birth must use the format YYYY-MM-DD.") from exc
    if parsed > date.today():
        raise ValueError("Date of birth cannot be in the future.")
    if parsed.year < 1900:
        raise ValueError("Date of birth must be after 1900.")
    return parsed.isoformat()


def validate_score(value: float) -> float:
    """Return a score between 0 and 100 as a float or raise ValueError."""
    try:
        score = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Score must be a number between 0 and 100.") from exc
    if not 0 <= score <= 100:
        raise ValueError("Score must be between 0 and 100.")
    return round(score, 2)


def format_date_of_birth(value: str) -> str:
    """Convert an ISO date string to a readable format."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d %B %Y")
    except (TypeError, ValueError):
        return value


class Student:
    """Represents a single student and their subject scores."""

    def __init__(
        self,
        student_id: str,
        full_name: str,
        form_class: str,
        gender: str,
        date_of_birth: str,
        scores: dict[str, float] | None = None,
        results_entered_at: str | None = None,
    ) -> None:
        self.student_id = validate_student_id(student_id)
        self.full_name = validate_name(full_name)
        self.form_class = validate_form(form_class)
        self.gender = validate_gender(gender)
        self.date_of_birth = validate_date_of_birth(date_of_birth)
        self.scores: dict[str, float] = {}
        self.results_entered_at = results_entered_at
        if scores:
            self.set_scores(scores)

    @property
    def has_scores(self) -> bool:
        return bool(self.scores)

    def set_scores(self, scores: dict[str, float]) -> None:
        """Replace all scores after validating them."""
        cleaned: dict[str, float] = {}
        for subject, score in scores.items():
            subject_name = str(subject).strip()
            if not subject_name:
                raise ValueError("Subject name cannot be empty.")
            cleaned[subject_name] = validate_score(score)
        self.scores = cleaned

    def update_score(self, subject: str, score: float) -> None:
        """Update one subject score."""
        subject_name = str(subject).strip()
        if not subject_name:
            raise ValueError("Subject name cannot be empty.")
        self.scores[subject_name] = validate_score(score)

    def update_details(self, **changes: str) -> None:
        """Validate and apply changes to personal details."""
        allowed = {"student_id", "full_name", "form_class", "gender", "date_of_birth"}
        unknown = set(changes) - allowed
        if unknown:
            raise ValueError(f"Unsupported field(s): {', '.join(sorted(unknown))}")

        validators = {
            "student_id": validate_student_id,
            "full_name": validate_name,
            "form_class": validate_form,
            "gender": validate_gender,
            "date_of_birth": validate_date_of_birth,
        }
        validated = {field: validators[field](value) for field, value in changes.items()}
        for field, value in validated.items():
            setattr(self, field, value)

    def to_dict(self) -> dict:
        """Return a JSON-friendly representation of the student."""
        return {
            "student_id": self.student_id,
            "full_name": self.full_name,
            "form_class": self.form_class,
            "gender": self.gender,
            "date_of_birth": self.date_of_birth,
            "scores": dict(self.scores),
            "results_entered_at": self.results_entered_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        """Build a Student from stored dictionary data."""
        if not isinstance(data, dict):
            raise ValueError("Each student record must be a dictionary.")

        student_id = data.get("student_id", data.get("id"))
        full_name = data.get("full_name", data.get("name"))
        form_class = data.get("form_class", data.get("form", data.get("class")))
        if form_class is None:
            form_class = data.get("class_name")
        gender = data.get("gender", "Other")
        date_of_birth = data.get("date_of_birth", data.get("dob"))

        missing = [
            label
            for label, value in (
                ("student_id", student_id),
                ("full_name", full_name),
                ("form_class", form_class),
                ("date_of_birth", date_of_birth),
            )
            if not value
        ]
        if missing:
            raise ValueError(f"Missing required field(s): {', '.join(missing)}")

        scores = data.get("scores") or {}
        if not isinstance(scores, dict):
            raise ValueError("Scores must be stored as a dictionary.")

        return cls(
            student_id=student_id,
            full_name=full_name,
            form_class=form_class,
            gender=gender,
            date_of_birth=date_of_birth,
            scores=scores,
            results_entered_at=data.get("results_entered_at"),
        )

    def __str__(self) -> str:
        return f"{self.student_id} - {self.full_name} ({self.form_class})"

    def __repr__(self) -> str:
        return f"Student(student_id={self.student_id!r}, full_name={self.full_name!r})"
