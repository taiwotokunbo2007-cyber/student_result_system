"""Text report cards, class summaries and CSV export."""

from __future__ import annotations

import csv
import os
from datetime import datetime

from results import (
    SUBJECTS,
    average_for,
    calculate_average,
    calculate_total,
    class_statistics,
    grade_for,
    grade_for_student,
    has_complete_results,
    position_of,
    ranked_students,
    remark_for,
    score_subjects,
    total_for,
)
from student import Student, format_date_of_birth

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
SCHOOL_NAME = "Bright Future Secondary School"


def _line(character: str = "=", width: int = 62) -> str:
    return character * width


def _table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "No records to display."

    widths = []
    for index, header in enumerate(headers):
        column_width = max(
            [len(header)] + [len(str(row[index])) for row in rows]
        )
        widths.append(min(column_width, 30))

    def render(values: list[str]) -> str:
        cells = []
        for value, width in zip(values, widths):
            text = str(value)
            if len(text) > width:
                text = text[: width - 1] + "."
            cells.append(text.ljust(width))
        return "  ".join(cells)

    header_line = render(headers)
    separator = "-" * len(header_line)
    body = [render([str(value) for value in row]) for row in rows]
    return "\n".join([header_line, separator, *body])


def summary_table(students: list[Student]) -> str:
    """Return a formatted table of students with totals, averages and grades."""
    if not students:
        return "No students registered yet."

    headers = [
        "Student ID",
        "Full Name",
        "Class",
        "Total",
        "Average",
        "Grade",
        "Complete",
    ]
    rows = []
    for student in students:
        if student.has_scores:
            total = f"{total_for(student):.2f}"
            average = f"{average_for(student):.2f}"
            grade = grade_for_student(student)
        else:
            total = average = grade = "-"
        complete = "Yes" if has_complete_results(student) else "No"
        rows.append(
            [
                student.student_id,
                student.full_name,
                student.form_class,
                total,
                average,
                grade,
                complete,
            ]
        )
    return _table(headers, rows)


def report_card(student: Student, classmates: list[Student] | None = None) -> str:
    """Return a complete text report card for one student."""
    lines = [
        _line(),
        SCHOOL_NAME.center(62),
        "STUDENT REPORT CARD".center(62),
        _line(),
        f"Student ID    : {student.student_id}",
        f"Full Name     : {student.full_name}",
        f"Class/Form    : {student.form_class}",
        f"Gender        : {student.gender}",
        f"Date of Birth : {format_date_of_birth(student.date_of_birth)}",
    ]

    if classmates is not None:
        position = position_of(student, classmates)
        if position is not None:
            lines.append(
                f"Class Position: {position} of {len(ranked_students(classmates))}"
            )

    lines.append(_line("-"))
    subject_rows = []
    for subject in score_subjects(student):
        score = student.scores.get(subject)
        if score is None:
            subject_rows.append([subject, "-", "-", "Not recorded"])
        else:
            subject_rows.append(
                [
                    subject,
                    f"{score:.2f}",
                    grade_for(score),
                    remark_for(score),
                ]
            )
    lines.append(_table(["Subject", "Score", "Grade", "Remark"], subject_rows))
    lines.append(_line("-"))

    total = calculate_total(student.scores)
    average = calculate_average(student.scores)
    lines.append(f"Total Score   : {total:.2f}")
    lines.append(f"Average Score : {average:.2f}")
    lines.append(f"Overall Grade : {grade_for_student(student)}")
    if student.has_scores:
        lines.append(f"Remark        : {remark_for(average)}")
    lines.append(f"Result Entered: {_format_timestamp(student.results_entered_at)}")
    lines.append(_line())
    return "\n".join(lines)


def _format_timestamp(value: str | None) -> str:
    if not value:
        return "Not recorded"
    try:
        return datetime.fromisoformat(value).strftime("%d %b %Y, %I:%M %p")
    except (TypeError, ValueError):
        return str(value)


def class_statistics_report(students: list[Student]) -> str:
    """Return a formatted class statistics report."""
    stats = class_statistics(students)
    lines = [_line(), "CLASS STATISTICS".center(62), _line()]
    lines.append(f"Students registered   : {stats['count']}")
    lines.append(f"Students with results : {stats['with_results']}")

    if not stats["with_results"]:
        lines.append("No scores have been recorded yet.")
        lines.append(_line())
        return "\n".join(lines)

    highest = stats["highest"]
    lowest = stats["lowest"]
    lines.append(
        f"Highest average       : {average_for(highest):.2f} "
        f"({highest.full_name}, {grade_for_student(highest)})"
    )
    lines.append(
        f"Lowest average        : {average_for(lowest):.2f} "
        f"({lowest.full_name}, {grade_for_student(lowest)})"
    )
    lines.append(f"Class average         : {stats['class_average']:.2f}")
    lines.append(f"Pass rate             : {stats['pass_rate']:.2f}%")
    lines.append("")
    lines.append("Grade Distribution")
    lines.append("-" * 30)
    for grade, count in stats["grade_distribution"].items():
        lines.append(f"  {grade}: {count}")

    if stats["subject_analysis"]:
        lines.append("")
        lines.append("Subject Analysis")
        rows = []
        for subject, data in stats["subject_analysis"].items():
            rows.append(
                [
                    subject,
                    data["entries"],
                    f"{data['average']:.2f}",
                    f"{data['highest']:.2f}",
                    f"{data['lowest']:.2f}",
                ]
            )
        lines.append(
            _table(
                ["Subject", "Entries", "Average", "Highest", "Lowest"],
                [[str(cell) for cell in row] for row in rows],
            )
        )

    lines.append(_line())
    return "\n".join(lines)


def build_full_report(students: list[Student]) -> str:
    """Return the complete text report for all students."""
    timestamp = datetime.now().strftime("%d %B %Y, %I:%M %p")
    sections = [
        _line(),
        SCHOOL_NAME.center(62),
        "STUDENT RESULT MANAGEMENT SYSTEM".center(62),
        f"Generated: {timestamp}".center(62),
        _line(),
        "",
        "ALL STUDENT RESULTS (sorted by average, highest first)",
        "",
        summary_table(ranked_students(students)),
        "",
        class_statistics_report(students),
    ]
    return "\n".join(sections)


def save_text_report(text: str, filename: str | None = None) -> str:
    """Save a report to the reports directory and return its path."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    name = filename or f"result_report_{datetime.now():%Y%m%d_%H%M%S}.txt"
    path = os.path.join(REPORTS_DIR, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
        if not text.endswith("\n"):
            handle.write("\n")
    return path


def export_summary_csv(students: list[Student], filename: str | None = None) -> str:
    """Export a spreadsheet-friendly CSV summary and return its path."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    name = filename or f"student_results_{datetime.now():%Y%m%d_%H%M%S}.csv"
    path = os.path.join(REPORTS_DIR, name)

    headers = [
        "Student ID",
        "Full Name",
        "Class",
        "Gender",
        "Date of Birth",
        *SUBJECTS,
        "Total",
        "Average",
        "Grade",
        "Results Entered",
    ]

    with open(path, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        for student in sorted(students, key=lambda item: item.full_name.lower()):
            row = [
                student.student_id,
                student.full_name,
                student.form_class,
                student.gender,
                student.date_of_birth,
            ]
            row.extend(
                f"{student.scores[subject]:.2f}" if subject in student.scores else ""
                for subject in SUBJECTS
            )
            if student.has_scores:
                row.extend(
                    [
                        f"{total_for(student):.2f}",
                        f"{average_for(student):.2f}",
                        grade_for_student(student),
                    ]
                )
            else:
                row.extend(["", "", ""])
            row.append(_format_timestamp(student.results_entered_at))
            writer.writerow(row)
    return path
