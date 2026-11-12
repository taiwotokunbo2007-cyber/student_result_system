"""Score calculation, grading, sorting and class statistics."""

from __future__ import annotations

from datetime import datetime

from student import Student, validate_score

SUBJECTS = (
    "Mathematics",
    "English Language",
    "Physics",
    "Chemistry",
    "Biology",
)

PASS_MARK = 40.0

GRADE_SCALE = (
    ("A", 70.0, "Excellent"),
    ("B", 60.0, "Very Good"),
    ("C", 50.0, "Good"),
    ("D", 40.0, "Pass"),
    ("F", 0.0, "Fail"),
)


def grade_for(score: float) -> str:
    """Return the letter grade for a score or average."""
    for grade, minimum, _ in GRADE_SCALE:
        if score >= minimum:
            return grade
    return "F"


def remark_for(score: float) -> str:
    """Return a short remark for a score or average."""
    for _, minimum, remark in GRADE_SCALE:
        if score >= minimum:
            return remark
    return "Fail"


def calculate_total(scores: dict[str, float]) -> float:
    """Return the sum of all recorded scores."""
    if not scores:
        return 0.0
    return round(sum(scores.values()), 2)


def calculate_average(scores: dict[str, float]) -> float:
    """Return the average of all recorded scores."""
    if not scores:
        return 0.0
    return round(sum(scores.values()) / len(scores), 2)


def total_for(student: Student) -> float:
    return calculate_total(student.scores)


def average_for(student: Student) -> float:
    return calculate_average(student.scores)


def grade_for_student(student: Student) -> str:
    return grade_for(average_for(student)) if student.has_scores else "N/A"


def has_complete_results(student: Student) -> bool:
    return all(subject in student.scores for subject in SUBJECTS)


def score_subjects(student: Student) -> list[str]:
    """Return the standard subjects plus any extra recorded subjects."""
    extras = sorted(subject for subject in student.scores if subject not in SUBJECTS)
    return list(SUBJECTS) + extras


def record_scores(student: Student, scores: dict[str, float]) -> None:
    """Add or update scores for a student and stamp the entry date."""
    if not scores:
        raise ValueError("At least one score is required.")
    validated = {subject: validate_score(score) for subject, score in scores.items()}
    student.scores.update(validated)
    student.results_entered_at = datetime.now().isoformat(timespec="seconds")


def sort_by_average(students: list[Student], descending: bool = True) -> list[Student]:
    """Sort students by average score with names as the tie-breaker."""
    if descending:
        return sorted(
            students,
            key=lambda student: (
                -average_for(student) if student.has_scores else 101.0,
                student.full_name.lower(),
            ),
        )
    return sorted(
        students,
        key=lambda student: (
            average_for(student) if student.has_scores else -1.0,
            student.full_name.lower(),
        ),
    )


def sort_by_name(students: list[Student]) -> list[Student]:
    return sorted(students, key=lambda student: student.full_name.lower())


def sort_by_class(students: list[Student]) -> list[Student]:
    return sorted(
        students,
        key=lambda student: (student.form_class.lower(), student.full_name.lower()),
    )


def ranked_students(students: list[Student]) -> list[Student]:
    """Return students with results ordered from best to worst average."""
    return sort_by_average([student for student in students if student.has_scores])


def position_of(student: Student, classmates: list[Student]) -> int | None:
    """Return the student's class position, or None when unranked."""
    for index, ranked in enumerate(ranked_students(classmates), start=1):
        if ranked.student_id == student.student_id:
            return index
    return None


def class_statistics(students: list[Student]) -> dict:
    """Return aggregate statistics and subject analysis for a class."""
    scored = [student for student in students if student.has_scores]
    stats = {
        "count": len(students),
        "with_results": len(scored),
        "highest": None,
        "lowest": None,
        "class_average": 0.0,
        "pass_rate": 0.0,
        "subject_analysis": {},
        "grade_distribution": {grade: 0 for grade, _, _ in GRADE_SCALE},
    }

    if not scored:
        return stats

    ranked = sort_by_average(scored)
    averages = [average_for(student) for student in scored]

    stats["highest"] = ranked[0]
    stats["lowest"] = ranked[-1]
    stats["class_average"] = round(sum(averages) / len(averages), 2)
    passed = sum(1 for average in averages if average >= PASS_MARK)
    stats["pass_rate"] = round((passed / len(averages)) * 100, 2)

    for student in scored:
        grade = grade_for(average_for(student))
        stats["grade_distribution"][grade] += 1

    analysis = {}
    for subject in SUBJECTS:
        values = [
            student.scores[subject]
            for student in scored
            if subject in student.scores
        ]
        if values:
            analysis[subject] = {
                "entries": len(values),
                "average": round(sum(values) / len(values), 2),
                "highest": max(values),
                "lowest": min(values),
            }
    stats["subject_analysis"] = analysis
    return stats
