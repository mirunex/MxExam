# MxExam

MxExam is a self-hosted exam platform for institutions. Teachers create exams, assign groups, import questions from Excel or PDF, review results, and monitor exam activity. Student data stays on the institution’s own server.

## Features

- Teacher, student, institution administrator, and system administrator accounts.
- Multiple-choice, written-response, and programming exams.
- Group-based exam assignment and scheduled start/end times.
- Student import from `.xlsx` files.
- Programming tasks imported from Excel, including the `Problems` workbook format (`Title`, `Description`, `Score`, `Solution`, and `Test Cases`).
- Python and Java code execution with public test-case verdicts and private grading tests.
- Live student presence, exam activity, anti-cheating events, and code submission history for teachers.
- English-language interface.

## Local setup

1. Create and activate a Python virtual environment.
2. Install the dependencies listed in `requirements.txt`.
3. Run database migrations with `python manage.py migrate`.
4. Create an administrator with `python manage.py createsuperuser`.
5. Start the server with `python manage.py runserver`.

## Excel programming-task workbook

For the academy-style `Problems` sheet, include these columns: `Name`, `Title`, `Description`, `Score`, `Examples`, `Solution`, and `Test Cases`. `Language` (`python` or `java`) and `Starter Code` are optional; the default language is Python. `Examples` may contain multiple `Input:` / `Output:` pairs. They are public and do not affect scores. The `Test Cases` generator uses the `INPUT ... END` format to create hidden grading cases. Optional translated columns may also be present; the student-facing interface displays the English title and description.

When students run their code, the response contains only public test cases. Hidden tests are evaluated on submission and are never sent to the student’s browser. Teachers can review the full submission history from the exam results page.

## Development

Run Django’s system checks with `python manage.py check`. Apply new schema migrations with `python manage.py migrate`.

For production, set `MXEXAM_PROD=1`, `DJANGO_ALLOWED_HOSTS`, and `DJANGO_CSRF_TRUSTED_ORIGINS` in the environment for the deployment host.
