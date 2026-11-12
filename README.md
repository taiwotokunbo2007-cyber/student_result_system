# Student Result Management System

A menu-driven Python application for a secondary school. It registers students,
records and updates subject scores, calculates totals, averages and grades,
produces report cards, analyses class performance, and stores everything in a
JSON data file.

Built as the Python Programming practical project.

## Features

### Student management
- Add a student with Student ID, full name, class/form, gender and date of birth
- View all registered students in a formatted table
- Search by student ID or name (exact or partial match)
- Update student information
- Delete a student and their scores

### Score and result management
- Record scores for five subjects: Mathematics, English Language, Physics,
  Chemistry and Biology
- Update existing scores (blank input keeps the current score)
- Calculate total and average scores
- Assign grades from the average:

  | Average | Grade | Remark |
  |---------|-------|--------|
  | 70 - 100 | A | Excellent |
  | 60 - 69 | B | Very Good |
  | 50 - 59 | C | Good |
  | 40 - 49 | D | Pass |
  | 0 - 39 | F | Fail |

- Display an individual report card, including class position
- Record the date and time results are entered

### Reporting and analysis
- List all students with totals, averages, grades and completion status
- Sort results by average (high to low or low to high), name or class
- Show class statistics: highest average, lowest average, class average,
  pass rate, grade distribution and per-subject analysis
- Save a full text report to the `reports/` folder
- Export a spreadsheet-friendly CSV summary to the `reports/` folder

### Data persistence
- All records are saved to `data/students.json` after every change
- Data is loaded automatically at start-up
- A missing data file starts an empty system without errors
- A corrupted data file is backed up and reported
- Saves are written atomically to reduce the risk of data loss

## Project structure

```text
student_result_system/
├── main.py              # Entry point and menu interface
├── student.py           # Student class and validation helpers
├── results.py           # Score, grade, sorting and statistics logic
├── storage.py           # JSON load and save functions
├── reports.py           # Report cards, statistics text and CSV export
├── data/
│   └── students.json    # Persistent student data
├── reports/             # Generated text reports and CSV files
├── README.md
└── .gitignore
```

## Requirements

- Python 3.10 or newer (tested with Python 3.12)
- No third-party packages; only the Python standard library is used

## How to run

1. Open a terminal in the project folder.
2. Run:

```bash
python main.py
```

On Windows, if `python` is not available, use:

```powershell
py main.py
```

3. Choose an option from the menu and follow the prompts. Enter `0` to exit.

### Example workflow

1. Choose `1` and register a student (for example ID `STU/2026/001`).
2. Choose `6` and enter scores for the five subjects.
3. Choose `7` to view the report card.
4. Choose `8` to view and sort all results.
5. Choose `9` to see class statistics.
6. Choose `10` to save a text report, or `11` to export a CSV.

## Data file

Student records are stored in `data/students.json` in this format:

```json
{
  "school": "Bright Future Secondary School",
  "saved_at": "2026-11-12T10:30:00",
  "students": [
    {
      "student_id": "STU/2026/001",
      "full_name": "Ada Okafor",
      "form_class": "SS1",
      "gender": "Female",
      "date_of_birth": "2009-04-18",
      "scores": {
        "Mathematics": 85.0,
        "English Language": 78.0,
        "Physics": 72.5,
        "Chemistry": 69.0,
        "Biology": 80.0
      },
      "results_entered_at": "2026-11-12T10:30:00"
    }
  ]
}
```

You may edit this file manually, but keep the JSON format valid.

## Validation rules

- Student ID: 3-20 characters using letters, digits, `/`, `_` or `-`
- Full name: 2-50 characters using letters, spaces, apostrophes, hyphens or periods
- Class/Form: 1-15 characters using letters, digits, spaces, `/` or `-`
- Gender: `Male`, `Female` or `Other`
- Date of birth: `YYYY-MM-DD`, not in the future and not before 1900
- Scores: numbers from 0 to 100

Regular expressions are used for Student ID, name and class validation.

## Python concepts demonstrated

- Variables, data types, type conversion and formatted output
- `if`/`elif`/`else`, `for` loops and `while` loops
- Lists, tuples and dictionaries
- Functions with parameters and return values
- Sorting with key functions
- Exception handling with `try`/`except`/`else`/`finally`
- File handling with `json` and `csv`
- Modules split across multiple Python files
- Object-oriented programming with the `Student` class
- Dates and times with `datetime`
- Standard library modules: `os`, `json`, `csv`, `re`, `datetime`, `sys`

## Notes for the instructor

- The application is fully offline and uses no external services.
- Generated report and CSV files are written to `reports/`. That folder is
  included with a placeholder so the path always exists.
- To start with a clean database, replace `data/students.json` with:

```json
{"students": []}
```

## Publishing to GitHub

The project is already organised for version control. To publish it:

```bash
git init
git add .
git commit -m "Build student result management system"
git branch -M main
git remote add origin https://github.com/<your-username>/student-result-system.git
git push -u origin main
```

Make additional commits as features are added, and confirm the repository is
accessible to the instructor.

## Author

- Name: Tokunbo
- Course: Python Programming
- Matriculation number: 24/sci01/199
