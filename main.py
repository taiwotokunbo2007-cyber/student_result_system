"""Entry point and menu-driven interface for the Student Result Management System."""

from __future__ import annotations

from reports import (
    SCHOOL_NAME,
    build_full_report,
    class_statistics_report,
    export_summary_csv,
    report_card,
    save_text_report,
    summary_table,
)
from results import (
    SUBJECTS,
    class_statistics,
    has_complete_results,
    record_scores as store_scores,
    sort_by_average,
    sort_by_class,
    sort_by_name,
)
from storage import DATA_FILE, StorageError, load_students, save_students
from student import (
    GENDERS,
    Student,
    validate_date_of_birth,
    validate_form,
    validate_gender,
    validate_name,
    validate_score,
    validate_student_id,
)

MENU = """
============================================================
  {school}
  STUDENT RESULT MANAGEMENT SYSTEM
============================================================
  1. Add a new student
  2. View all students
  3. Search for a student
  4. Update student information
  5. Delete a student
  6. Record / update scores
  7. View a student's report card
  8. List all results (sortable)
  9. Class statistics
 10. Save text report to file
 11. Export results to CSV
  0. Exit
============================================================"""


def show_menu() -> None:
    print(MENU.format(school=SCHOOL_NAME))


def prompt_validated(label: str, validator):
    """Prompt until the validator accepts a value; blank cancels."""
    while True:
        raw = input(label).strip()
        if not raw:
            return None
        try:
            return validator(raw)
        except ValueError as exc:
            print(f"  {exc}")


def prompt_gender():
    while True:
        raw = input("Gender (Male/Female/Other, blank to cancel): ").strip()
        if not raw:
            return None
        for gender in GENDERS:
            if raw.lower() == gender.lower():
                return gender
        print("  Please enter Male, Female or Other.")


def confirm(message: str) -> bool:
    return input(message).strip().lower() in {"y", "yes"}


def persist(students: list[Student]) -> bool:
    """Save students, reporting any storage failure."""
    try:
        save_students(students)
    except StorageError as exc:
        print(f"Warning: data could not be saved. {exc}")
        return False
    else:
        return True


def search_matches(students: list[Student], term: str) -> list[Student]:
    key = term.strip().lower()
    if not key:
        return []
    exact = [
        student
        for student in students
        if student.student_id.lower() == key or student.full_name.lower() == key
    ]
    if exact:
        return exact
    return [
        student
        for student in students
        if key in student.student_id.lower() or key in student.full_name.lower()
    ]


def select_student(students: list[Student]) -> Student | None:
    if not students:
        print("No students are registered yet.")
        return None

    term = input("Enter student ID or name: ").strip()
    if not term:
        print("No search term entered.")
        return None

    matches = search_matches(students, term)
    if not matches:
        print("No matching student found.")
        return None
    if len(matches) == 1:
        return matches[0]

    print("Multiple matches found:")
    for index, student in enumerate(matches, start=1):
        print(f"  {index}. {student}")
    choice = input("Choose a number (blank to cancel): ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(matches):
        print("No student selected.")
        return None
    return matches[int(choice) - 1]


def add_student(students: list[Student]) -> None:
    print("\n--- Add New Student ---")
    student_id = prompt_validated("Student ID (blank to cancel): ", validate_student_id)
    if student_id is None:
        print("Add student cancelled.")
        return
    if any(student.student_id.lower() == student_id.lower() for student in students):
        print("A student with that ID already exists.")
        return

    full_name = prompt_validated("Full name: ", validate_name)
    if full_name is None:
        print("Add student cancelled.")
        return
    form_class = prompt_validated("Class/Form (e.g. SS1): ", validate_form)
    if form_class is None:
        print("Add student cancelled.")
        return
    gender = prompt_gender()
    if gender is None:
        print("Add student cancelled.")
        return
    date_of_birth = prompt_validated(
        "Date of birth (YYYY-MM-DD): ", validate_date_of_birth
    )
    if date_of_birth is None:
        print("Add student cancelled.")
        return

    try:
        student = Student(student_id, full_name, form_class, gender, date_of_birth)
    except ValueError as exc:
        print(f"Could not add student: {exc}")
    else:
        students.append(student)
        if persist(students):
            print(f"Student {student.full_name} was added successfully.")
    finally:
        print(f"Total registered students: {len(students)}")


def view_students(students: list[Student]) -> None:
    print("\n--- Registered Students ---")
    if not students:
        print("No students are registered yet.")
        return
    print(summary_table(sort_by_name(students)))


def search_students(students: list[Student]) -> None:
    print("\n--- Search Students ---")
    term = input("Enter all or part of a student ID or name: ").strip()
    if not term:
        print("No search term entered.")
        return
    matches = search_matches(students, term)
    if not matches:
        print("No matching student found.")
        return
    print(f"{len(matches)} match(es) found:")
    print(summary_table(sort_by_name(matches)))


def update_student(students: list[Student]) -> None:
    print("\n--- Update Student Information ---")
    student = select_student(students)
    if student is None:
        return

    print(f"\nSelected: {student}")
    print(f"  Full name     : {student.full_name}")
    print(f"  Class/Form    : {student.form_class}")
    print(f"  Gender        : {student.gender}")
    print(f"  Date of birth : {student.date_of_birth}")
    print(f"  Student ID    : {student.student_id}")
    print("\n  1. Full name")
    print("  2. Class/Form")
    print("  3. Gender")
    print("  4. Date of birth")
    print("  5. Student ID")
    print("  0. Cancel")

    fields = {
        "1": ("full_name", "full name", validate_name),
        "2": ("form_class", "class/form", validate_form),
        "3": ("gender", "gender (Male/Female/Other)", validate_gender),
        "4": ("date_of_birth", "date of birth (YYYY-MM-DD)", validate_date_of_birth),
        "5": ("student_id", "student ID", validate_student_id),
    }
    choice = input("Select the field to update: ").strip()
    if choice == "0" or choice not in fields:
        print("Update cancelled.")
        return

    field, label, validator = fields[choice]
    new_value = prompt_validated(f"New {label} (blank to cancel): ", validator)
    if new_value is None:
        print("Update cancelled.")
        return

    if field == "student_id":
        duplicate = any(
            other is not student
            and other.student_id.lower() == new_value.lower()
            for other in students
        )
        if duplicate:
            print("Another student already uses that ID.")
            return

    try:
        student.update_details(**{field: new_value})
    except ValueError as exc:
        print(f"Update failed: {exc}")
    else:
        if persist(students):
            print(f"{student.full_name}'s {label} was updated.")


def delete_student(students: list[Student]) -> None:
    print("\n--- Delete Student ---")
    student = select_student(students)
    if student is None:
        return
    print(f"Selected: {student}")
    if not confirm("Delete this student and all scores? [y/N]: "):
        print("Delete cancelled.")
        return
    students.remove(student)
    if persist(students):
        print(f"{student.full_name} was deleted.")


def record_scores(students: list[Student]) -> None:
    print("\n--- Record / Update Scores ---")
    student = select_student(students)
    if student is None:
        return

    print(f"\nStudent: {student.full_name} ({student.student_id})")
    print("Leave a score blank to keep it unchanged. Type 'c' to cancel.\n")

    entered: dict[str, float] = {}
    for subject in SUBJECTS:
        current = student.scores.get(subject)
        suffix = f" [current: {current:.2f}]" if current is not None else ""
        while True:
            raw = input(f"{subject}{suffix}: ").strip()
            if raw.lower() == "c":
                print("Score entry cancelled.")
                return
            if not raw:
                break
            try:
                entered[subject] = validate_score(raw)
            except ValueError as exc:
                print(f"  {exc}")
            else:
                break

    if not entered:
        print("No scores entered.")
        return

    print("\nScores to save:")
    for subject, score in entered.items():
        print(f"  {subject}: {score:.2f}")
    if not confirm("Save these scores? [y/N]: "):
        print("Changes discarded.")
        return

    try:
        store_scores(student, entered)
    except ValueError as exc:
        print(f"Could not record scores: {exc}")
    else:
        if persist(students):
            print(f"Scores saved for {student.full_name}.")
            print(
                "Result completeness: "
                + ("complete" if has_complete_results(student) else "incomplete")
            )


def view_report_card(students: list[Student]) -> None:
    print("\n--- Student Report Card ---")
    student = select_student(students)
    if student is None:
        return
    print(report_card(student, classmates=students))


def list_results(students: list[Student]) -> None:
    print("\n--- List All Results ---")
    if not students:
        print("No students are registered yet.")
        return

    print("Sort by:")
    print("  1. Average score (highest to lowest) [default]")
    print("  2. Average score (lowest to highest)")
    print("  3. Full name (A-Z)")
    print("  4. Class/Form")
    choice = input("Select an option: ").strip() or "1"

    if choice == "1":
        ordered = sort_by_average(students, descending=True)
        label = "average (highest to lowest)"
    elif choice == "2":
        ordered = sort_by_average(students, descending=False)
        label = "average (lowest to highest)"
    elif choice == "3":
        ordered = sort_by_name(students)
        label = "name (A-Z)"
    elif choice == "4":
        ordered = sort_by_class(students)
        label = "class/form"
    else:
        print("Invalid option; using the default sort.")
        ordered = sort_by_average(students, descending=True)
        label = "average (highest to lowest)"

    print(f"\nResults sorted by {label}:")
    print(summary_table(ordered))


def show_class_statistics(students: list[Student]) -> None:
    print("\n--- Class Statistics ---")
    stats = class_statistics(students)
    print(f"Registered students: {stats['count']}")
    print(f"Students with results: {stats['with_results']}")
    print(class_statistics_report(students))


def save_report_file(students: list[Student]) -> None:
    print("\n--- Save Text Report ---")
    if not students:
        print("No students are registered yet.")
        return
    try:
        path = save_text_report(build_full_report(students))
    except OSError as exc:
        print(f"Could not save the report: {exc}")
    else:
        print(f"Report saved to: {path}")
    finally:
        print("Report operation complete.")


def export_csv_file(students: list[Student]) -> None:
    print("\n--- Export Results to CSV ---")
    if not students:
        print("No students are registered yet.")
        return
    try:
        path = export_summary_csv(students)
    except OSError as exc:
        print(f"Could not export CSV: {exc}")
    else:
        print(f"CSV exported to: {path}")
    finally:
        print("CSV export operation complete.")


def handle_choice(choice: str, students: list[Student]) -> None:
    if choice == "1":
        add_student(students)
    elif choice == "2":
        view_students(students)
    elif choice == "3":
        search_students(students)
    elif choice == "4":
        update_student(students)
    elif choice == "5":
        delete_student(students)
    elif choice == "6":
        record_scores(students)
    elif choice == "7":
        view_report_card(students)
    elif choice == "8":
        list_results(students)
    elif choice == "9":
        show_class_statistics(students)
    elif choice == "10":
        save_report_file(students)
    elif choice == "11":
        export_csv_file(students)
    else:
        print("Invalid option. Please choose a number from the menu.")


def run() -> None:
    print(f"\nWelcome to the {SCHOOL_NAME} result system.")

    students: list[Student] = []
    try:
        students = load_students()
    except StorageError as exc:
        print(f"Warning: {exc}")
        print("Starting with an empty student list.")
    else:
        print(f"Loaded {len(students)} registered student(s).")
    finally:
        print(f"Data file: {DATA_FILE}")

    while True:
        show_menu()
        try:
            choice = input("Select an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if choice == "0":
            print("Goodbye. All changes are saved.")
            break

        try:
            handle_choice(choice, students)
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled. Returning to the main menu.")
        except Exception as exc:
            print(f"An unexpected error occurred: {exc}")


if __name__ == "__main__":
    run()
