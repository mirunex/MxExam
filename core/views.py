import random
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from pypdf import PdfReader
from core.forms import (GroupForm, AdminGroupForm, ExamForm, InstitutionForm, PDFUploadForm, TeacherForm, StudentForm)
from core.models import Group, ExamSession, Answer
from core.models.exam import Exam
from core.models.question import Question
from core.models.result import ExamResult
from core.services.pdf_import import parse_test_questions, parse_written_questions
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from core.models import Institution
from core.forms import InstitutionAdminForm
from core.code_import import parse_code_tasks
from core.code_runner import run_python
from core.models import CodeTask, CodeTestCase
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from core.code_runner import check_task
from core.models import CodeSubmission, CodeSubmissionAttempt
from core.excel_import import parse_students_excel
from django.db.models import Count
from django.utils import timezone
from core.models import Violation
from datetime import timedelta
from django.utils.dateparse import parse_datetime
from core.models import ExamEvent
from core.code_runner import run_code
from core.excel_tasks import parse_tasks_excel
from core.task_build import build_tests

User = get_user_model()

def role_login_view(request, allowed_roles, title, subtitle):
    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user and user.role in allowed_roles:
            login(request, user)
            return redirect('dashboard')

        error = 'The username, password, or account type is incorrect.'

    return render(request, 'login.html', {
        'error': error,
        'login_title': title,
        'login_subtitle': subtitle,
    })


def user_login_view(request):
    return role_login_view(
        request,
        ('teacher', 'student'),
        'MxExam',
        'Teacher and student sign-in',
    )


def admin_login_view(request):
    return role_login_view(
        request,
        ('admin',),
        'MxExam Admin',
        'Institution administrator sign-in',
    )


def superadmin_login_view(request):
    return role_login_view(
        request,
        ('superadmin',),
        'MxExam Control',
        'System super administrator sign-in',
    )

@login_required
def admin_dashboard(request):
    if not request.user.is_admin():
        return redirect('dashboard')

    institution = request.user.institution

    context = {
        'institution': institution,
        'teacher_count': User.objects.filter(
            institution=institution, role='teacher'
        ).count(),
        'student_count': User.objects.filter(
            institution=institution, role='student'
        ).count(),
    }

    return render(request, 'admin_dashboard.html', context)

@login_required
def institution_admin_create_view(request, institution_id):
    # Superadmin yoxlaması
    if not request.user.is_superadmin():
        return redirect('dashboard')

    institution = get_object_or_404(Institution, id=institution_id)

    if request.method == 'POST':
        form = InstitutionAdminForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'admin'
            user.institution = institution
            user.save()

            messages.success(
                request,
                f"'{institution.name}'  administrator created successfully.",
            )
            return redirect('superadmin_dashboard')
    else:
        form = InstitutionAdminForm()

    return render(
        request,
        'institution_admin_create.html',
        {
            'form': form,
            'institution': institution,
        },
    )
@login_required
def teacher_create_view(request):

    if not request.user.is_admin():
        return redirect('dashboard')

    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'teacher'
            user.institution = request.user.institution  
            user.save()

            messages.success(request, "Teacher created successfully.")
            return redirect('admin_dashboard')
    else:
        form = TeacherForm()

    return render(request, 'teacher_create.html', {'form': form})
@login_required
def admin_groups_view(request):
    if not request.user.is_admin():
        return redirect('dashboard')

    institution = request.user.institution

    if request.method == 'POST':
        form = AdminGroupForm(
            request.POST,
            institution=institution,
        )

        if form.is_valid():
            group = form.save(commit=False)
            group.institution = institution
            group.save()

            messages.success(
                request,
                f"'{group.name}' group created successfully.",
            )
            return redirect('admin_groups')
    else:
        form = AdminGroupForm(institution=institution)

    groups = Group.objects.filter(
        institution=institution,
    ).select_related('teacher').order_by('name')

    return render(request, 'admin_groups.html', {
        'group_form': form,
        'groups': groups,
    })
@login_required
def institution_create_view(request):
    # Superadmin yoxlaması
    if not request.user.is_superadmin():
        return redirect('dashboard')

    if request.method == 'POST':
        form = InstitutionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Institution created successfully.")
            return redirect('superadmin_dashboard')
    else:
        form = InstitutionForm()

    return render(request, 'institution_create.html', {'form': form})
@login_required
def dashboard_view(request):
    if request.user.is_teacher():
        return redirect('teacher_dashboard')
    
    if request.user.is_superadmin():
        return redirect('superadmin_dashboard')
    
    if request.user.is_admin():
        return redirect('admin_dashboard')
    return redirect('student_dashboard')

@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher():
        return redirect('student_dashboard')

    exams = Exam.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'teacher_dashboard.html', {'exams': exams})



@login_required
def superadmin_dashboard(request):

    if not request.user.is_superadmin():
        return redirect('dashboard')

    institutions = Institution.objects.all()

    context = {
        'institutions': institutions,
        'institution_count': institutions.count(),
        'admin_count': User.objects.filter(role='admin').count(),
        'teacher_count': User.objects.filter(role='teacher').count(),
        'student_count': User.objects.filter(role='student').count(),
    }

    return render(request, 'superadmin_dashboard.html', context)

@login_required
def create_exam_view(request):
    if not request.user.is_teacher():
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = ExamForm(request.POST, teacher=request.user)
        pdf_form = PDFUploadForm(request.POST, request.FILES)
        form_ok = form.is_valid()
        pdf_ok = pdf_form.is_valid()

        if form_ok and pdf_ok:
            exam_type = form.cleaned_data.get('exam_type')
            question_type = exam_type if exam_type in ('written', 'code') else 'test'

            questions = []
            code_tasks = []
            errors = []
            full_text = ""

            upload = pdf_form.cleaned_data['pdf_file']
            is_excel = upload.name.lower().endswith('.xlsx')

            try:
                if question_type == 'code' and not is_excel:
                    pdf_form.add_error('pdf_file', 'Upload an Excel (.xlsx) file for a coding exam.')
                    full_text = None
                elif question_type != 'code' and is_excel:
                    pdf_form.add_error('pdf_file', 'Upload a PDF file for this exam type.')
                    full_text = None
                elif question_type == 'code':
                    code_tasks, errors = parse_tasks_excel(upload)
                    full_text = "excel"
                else:
                    reader = PdfReader(upload)
                    full_text = "\n".join(
                        page.extract_text() or "" for page in reader.pages
                    )
                    if question_type == 'written':
                        questions, errors = parse_written_questions(full_text)
                    else:
                        questions, errors = parse_test_questions(full_text)
            except Exception:
                pdf_form.add_error('pdf_file', 'Could not read the file.')
                full_text = None


            if full_text is not None:
                # Kod imtahanı: testləri hazırla (çıxışı olmayanlar etalon kodla hesablanır)
                if question_type == 'code' and not errors:
                    for i, task in enumerate(code_tasks, start=1):
                        errors += build_tests(i, task)

                found = code_tasks if question_type == 'code' else questions

                if not full_text.strip() or (not found and not errors):
                    pdf_form.add_error(
                        'pdf_file', 'No questions in the expected format were found in the PDF.'
                    )
                elif errors:
                    for error in errors:
                        pdf_form.add_error('pdf_file', error)
                else:
                    with transaction.atomic():
                        exam = form.save(commit=False)
                        exam.created_by = request.user
                        exam.save()
                        form.save_m2m()

                        if question_type == 'code':
                            for task in code_tasks:
                                ct = CodeTask.objects.create(
                                    exam=exam,
                                    language=task.get('language', 'python'),
                                    title=task['title'],
                                    title_en=task.get('title_en', ''),
                                    title_ru=task.get('title_ru', ''),
                                    description=task['description'],
                                    description_en=task.get('description_en', ''),
                                    description_ru=task.get('description_ru', ''),
                                    reference_code=task['reference_code'],
                                    points=task['points'],
                                    starter_code=task['starter_code'],
                                )
                                CodeTestCase.objects.bulk_create([
                                    CodeTestCase(
                                        task=ct, input_data=inp, expected_output=out,
                                        is_hidden=hidden,
                                    )
                                    for inp, out, hidden in task['tests']
                                ])
                        else:
                            Question.objects.bulk_create([
                                Question(
                                    exam=exam,
                                    created_by=request.user,
                                    question_type=question_type,
                                    **q,
                                )
                                for q in questions
                            ])
                    messages.success(request, "Exam created successfully.")
                    return redirect('teacher_dashboard')
    else:
        form = ExamForm(teacher=request.user)
        pdf_form = PDFUploadForm()

    return render(request, 'exam_create.html', {
        'exam_form': form,
        'pdf_form': pdf_form,
    })

@login_required
def student_create_view(request):
    if not request.user.is_admin():
        return redirect('dashboard')

    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'student'
            user.institution = request.user.institution
            user.save()
            messages.success(request, "Student created successfully.")
            return redirect('admin_dashboard')
    else:
        form = StudentForm()

    return render(request, 'student_create.html', {'form': form})

@login_required
def student_import_view(request):
    if not request.user.is_admin() or request.user.institution is None:
        return redirect('dashboard')

    institution = request.user.institution

    if request.method == 'POST':
        file = request.FILES.get('excel_file')

        if file is None:
            messages.error(request, "No file was selected.")
        elif not file.name.lower().endswith('.xlsx'):
            messages.error(request, "Only .xlsx files are accepted.")
        elif file.size > 2 * 1024 * 1024:
            messages.error(request, "The file must not exceed 2 MB.")
        else:
            group_names = set(
                Group.objects.filter(institution=institution).values_list('name', flat=True)
            )
            existing = {
                u: (r, i)
                for u, r, i in User.objects.values_list('username', 'role', 'institution_id')
            }
            rows, fatal = parse_students_excel(file, group_names, existing, institution.id)

            if fatal:
                messages.error(request, fatal)
            else:
                valid = [r for r in rows if not r['errors']]
                request.session['import_rows'] = valid
                return render(request, 'student_import.html', {
                    'rows': rows,
                    'ok_count': len(valid),
                    'error_count': len(rows) - len(valid),
                    'preview': True,
                })

    return render(request, 'student_import.html', {'preview': False})


@login_required
def student_import_confirm_view(request):
    if not request.user.is_admin() or request.user.institution is None:
        return redirect('dashboard')
    if request.method != 'POST':
        return redirect('student_import')

    institution = request.user.institution
    rows = request.session.pop('import_rows', None)
    if not rows:
        messages.error(request, "The upload session expired. Upload the file again.")
        return redirect('student_import')

    created = added = skipped = 0
    with transaction.atomic():
        for row in rows:
            group = Group.objects.filter(
                name=row['group'], institution=institution
            ).first()
            if group is None:
                skipped += 1
                continue

            user = User.objects.filter(username=row['username']).first()
            if user is None:
                user = User.objects.create_user(
                    username=row['username'],
                    password=row['password'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    role='student',
                    institution=institution,
                )
                created += 1
            elif user.role == 'student' and user.institution_id == institution.id:
                added += 1
            else:
                skipped += 1
                continue

            group.students.add(user)

    messages.success(
        request,
        f"New students: {created}; existing students added to groups: {added}; skipped: {skipped}.",
    )
    return redirect('admin_dashboard')

@login_required
def grade_written_view(request, exam_id, student_id):
    if not request.user.is_teacher():
        return redirect('dashboard')

    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    student = get_object_or_404(User, id=student_id)
    result = get_object_or_404(ExamResult, exam=exam, student=student)

    answers = (
        Answer.objects
        .filter(student=student, question__exam=exam, question__question_type='written')
        .select_related('question')
        .order_by('question_id')
    )

    if request.method == 'POST':
        for a in answers:
            raw = request.POST.get(f'points_{a.id}', '').strip().replace(',', '.')
            if raw == '':
                continue
            try:
                value = float(raw)
            except ValueError:
                continue
            a.awarded_points = max(0.0, min(value, a.question.points))
            a.save()

        # Yekun nəticəni yenidən hesabla
        all_answers = Answer.objects.filter(
            student=student, question__exam=exam
        ).select_related('question')
        result.score = sum(x.awarded_points or 0 for x in all_answers)
        result.total = sum(x.question.points for x in all_answers)
        result.save()

        messages.success(request, "Scores saved.")
        return redirect('exam_results', exam_id=exam.id)

    return render(request, 'grade_written.html', {
        'exam': exam,
        'student': student,
        'result': result,
        'answers': answers,
    })

@login_required
def teacher_groups(request):
    if not request.user.is_teacher():
        return redirect('student_dashboard')

    institution = request.user.institution
    if institution is None:
        groups = Group.objects.none()
    else:
        groups = (
            Group.objects.filter(institution=institution, teacher=request.user)
            .select_related('teacher')
            .prefetch_related('students')
            .order_by('name')
        )

    return render(request, 'teacher_groups.html', {'groups': groups})


@login_required
def teacher_group_detail(request, group_id):
    if not request.user.is_teacher() or request.user.institution is None:
        return redirect('dashboard')

    group = get_object_or_404(
        Group.objects.prefetch_related('students'),
        id=group_id,
        institution=request.user.institution,
        teacher=request.user,
    )

    if request.method == 'POST':
        student = group.students.filter(
            id=request.POST.get('student_id'), role='student'
        ).first()
        password = request.POST.get('new_password', '')
        confirmation = request.POST.get('confirm_password', '')

        if student is None:
            messages.error(request, 'That student is not in your group.')
        elif len(password) < 6:
            messages.error(request, 'The new password must be at least 6 characters.')
        elif password != confirmation:
            messages.error(request, 'The passwords do not match.')
        else:
            student.set_password(password)
            student.save(update_fields=['password'])
            messages.success(
                request,
                f'Password updated for {student.get_full_name() or student.username}.',
            )
        return redirect('teacher_group_detail', group_id=group.id)

    students = group.students.filter(role='student').order_by(
        'last_name', 'first_name', 'username'
    )
    return render(request, 'teacher_group_detail.html', {
        'group': group,
        'students': students,
    })


@login_required
def student_dashboard(request):
    if request.user.is_teacher():
        return redirect('teacher_dashboard')

    exams = Exam.objects.filter(groups__students=request.user).distinct()
    exams = [e for e in exams if not e.has_ended()]

    results = {
        r.exam_id: r
        for r in ExamResult.objects.filter(student=request.user)
    }
    for exam in exams:
        exam.result = results.get(exam.id)

    return render(request, 'student_dashboard.html', {
        'exams': exams,
    })


@login_required
def delete_exam_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    if request.method == 'POST':
        exam.delete()
    return redirect('teacher_dashboard')


@login_required
def add_question_view(request, exam_id):
    if not request.user.is_teacher():
        return redirect('student_dashboard')
    get_object_or_404(Exam, id=exam_id, created_by=request.user)
    return redirect('teacher_dashboard')


@login_required
def upload_exam_pdf(request, exam_id):
    if not request.user.is_teacher():
        return redirect("student_dashboard")
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    form = PDFUploadForm()
    if request.method == "POST":
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                reader = PdfReader(form.cleaned_data["pdf_file"])
                full_text = "\n".join(
                    page.extract_text() or "" for page in reader.pages
                )
            except Exception:
                form.add_error("pdf_file", "Could not read the PDF file.")
            else:
                if not full_text.strip():
                    form.add_error(
                        "pdf_file",
                        "No text could be extracted from the PDF. Scanned PDFs are not supported.",
                    )
                else:
                    questions, errors = parse_test_questions(full_text)
                    can_confirm = bool(questions) and not errors

                    if can_confirm:
                        request.session[f"pdf_preview_{exam.id}"] = questions
                    return render(request, "pdf_preview.html", {
                        "exam": exam,
                        "questions": questions,
                        "errors": errors,
                        "can_confirm": can_confirm,
                    })
    return render(request, "pdf_upload.html", {
        "exam": exam,
        "exam_form": form,
    })


@login_required
def start_exam_view(request, exam_id):
    if request.user.role != 'student':
        return redirect('dashboard')

    exam = get_object_or_404(
        Exam,
        id=exam_id,
        groups__students=request.user,
    )
    # Artıq təhvil verilibsə
    if ExamResult.objects.filter(student=request.user, exam=exam).exists():
        return redirect('student_dashboard')

    # İmtahan vaxtı yoxlanışı (POST üçün 30 saniyə güzəşt)
    if not exam.is_open(grace_seconds=30):
        return redirect('student_dashboard')

    session, created = ExamSession.objects.get_or_create(
        student=request.user, exam=exam
    )
    session.last_seen_at = timezone.now()
    session.save(update_fields=["last_seen_at"])

    if request.method == 'GET' and not created and not exam.allow_reentry:
        return redirect('student_dashboard')

 
    if created:
        pool = list(exam.questions.all())
        n = exam.questions_per_student
        chosen = random.sample(pool, n) if n and n < len(pool) else pool
        session.questions.set(chosen)

       
    if exam.exam_type == 'code':
        tasks = list(exam.code_tasks.all().order_by('id'))
        subs = {
            s.task_id: s
            for s in CodeSubmission.objects.filter(student=request.user, task__in=tasks)
        }

        if request.method == 'POST':
            score = 0.0
            total = 0.0
            for task in tasks:
                code = request.POST.get(f'code_{task.id}', '')
                passed, count = check_task(task, code)
                earned = task.points * passed / count if count else 0.0
                CodeSubmissionAttempt.objects.create(
                    student=request.user, task=task, code=code,
                    passed=passed, total=count, score=earned,
                )
                CodeSubmission.objects.update_or_create(
                    student=request.user, task=task,
                    defaults={'code': code, 'passed': passed, 'total': count, 'score': earned},
                )
                score += earned
                total += task.points
            ExamResult.objects.update_or_create(
                student=request.user, exam=exam,
                defaults={'score': score, 'total': total},
            )
            return redirect('student_dashboard')

        for task in tasks:
            task.sub = subs.get(task.id)
            task.initial_code = task.sub.code if task.sub else task.starter_code
            task.t_az = task.title
            task.t_en = task.title_en or task.title
            task.t_ru = task.title_ru or task.title_en or task.title
            task.d_az = task.description or task.description_en
            task.d_en = task.description_en or task.description
            task.d_ru = task.description_ru or task.description_en or task.description

        return render(request, 'take_code_exam.html', {
            'exam': exam,
            'tasks': tasks,
            'remaining_seconds': exam.remaining_seconds(),
        })

    questions = session.questions.all()

    if request.method == 'POST':
        score = 0.0
        total = 0.0

        for question in questions:
            total += question.points
            value = request.POST.get(f'question_{question.id}', '').strip()

            if question.question_type == 'written':
                # Yazılı: mətn saxlanır, bal müəllim yoxlayanda verilir
                Answer.objects.update_or_create(
                    student=request.user, question=question,
                    defaults={'text_answer': value, 'selected_option': '', 'awarded_points': None},
                )
            else:
                # Test: avtomatik yoxlanır
                earned = question.calculate_score(value) or 0.0
                score += earned
                Answer.objects.update_or_create(
                    student=request.user, question=question,
                    defaults={'selected_option': value.upper()[:1], 'text_answer': '', 'awarded_points': earned},
                )

        ExamResult.objects.update_or_create(
            student=request.user, exam=exam,
            defaults={'score': score, 'total': total},
        )
        return redirect('student_dashboard')

    return render(request, 'take_exam.html', {
        'exam': exam,
        'questions': questions,
        'remaining_seconds': exam.remaining_seconds(),
    })
@login_required
def exam_results_view(request, exam_id):
    if not request.user.is_teacher():
        return redirect('student_dashboard')
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    students = User.objects.filter(role='student', student_groups__exams=exam).distinct().order_by('last_name', 'first_name', 'username')
    results_by_id = {r.student_id: r for r in exam.results.select_related('student')}
    sessions_by_id = {s.student_id: s for s in exam.sessions.select_related('student')}
    roster = []
    for student in students:
        student.exam_result = results_by_id.get(student.id)
        student.exam_session = sessions_by_id.get(student.id)
        student.is_online = bool(student.exam_session and student.exam_session.last_seen_at and student.exam_session.last_seen_at >= timezone.now() - timedelta(seconds=45) and not student.exam_result)
        student.violation_count = Violation.objects.filter(student=student, exam=exam).count()
        student.submission_count = CodeSubmissionAttempt.objects.filter(student=student, task__exam=exam).count()
        roster.append(student)
    return render(request, 'exam_results.html', {'exam': exam, 'results': roster})


@login_required
def teacher_student_detail_view(request, exam_id, student_id):
    if not request.user.is_teacher():
        return redirect('dashboard')
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    student = get_object_or_404(User, id=student_id, role='student', student_groups__exams=exam)
    session = ExamSession.objects.filter(student=student, exam=exam).first()
    attempts = CodeSubmissionAttempt.objects.filter(student=student, task__exam=exam).select_related('task')
    events = ExamEvent.objects.filter(student=student, exam=exam)
    violations = Violation.objects.filter(student=student, exam=exam)
    timeline = []
    for event in events:
        if event.kind == 'run':
            text = f"Ran task {event.task_number} ({event.passed}/{event.total} public tests passed)"
        else:
            text = f"Submitted task {event.task_number} ({event.score:g}/{event.max_score:g} points)"
        timeline.append({'created_at': event.created_at, 'text': text})
    violation_labels = {'tab_hidden': 'Switched to another tab', 'window_blur': 'Left the exam window', 'paste': 'Pasted text'}
    for violation in violations:
        timeline.append({'created_at': violation.created_at, 'text': violation_labels.get(violation.kind, violation.kind)})
    if session:
        timeline.append({'created_at': session.started_at, 'text': 'Started the exam'})
    result = ExamResult.objects.filter(student=student, exam=exam).first()
    if result:
        timeline.append({'created_at': result.submitted_at, 'text': 'Submitted the exam'})
    timeline.sort(key=lambda item: item['created_at'], reverse=True)
    return render(request, 'teacher_student_detail.html', {'exam': exam, 'student': student, 'session': session, 'attempts': attempts, 'timeline': timeline, 'result': result})


@login_required
@require_POST
def exam_presence_view(request, exam_id):
    if request.user.role != 'student':
        return JsonResponse({'error': 'Not allowed.'}, status=403)
    session = ExamSession.objects.filter(student=request.user, exam_id=exam_id, exam__groups__students=request.user).first()
    if not session or ExamResult.objects.filter(student=request.user, exam_id=exam_id).exists():
        return JsonResponse({'ok': False}, status=404)
    session.last_seen_at = timezone.now()
    session.save(update_fields=['last_seen_at'])
    return JsonResponse({'ok': True})

@login_required
@require_POST
def run_code_view(request, exam_id):
    if request.user.role != 'student':
        return JsonResponse({'error': 'Not allowed.'}, status=403)
    exam = get_object_or_404(Exam, id=exam_id, exam_type='code', groups__students=request.user)
    if ExamResult.objects.filter(student=request.user, exam=exam).exists() or not exam.is_open(grace_seconds=30):
        return JsonResponse({'error': 'This exam is closed.'}, status=403)
    try:
        data = json.loads(request.body)
        task = CodeTask.objects.filter(id=int(data.get('task_id')), exam=exam).first()
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid request.'}, status=400)
    if task is None:
        return JsonResponse({'error': 'Task not found.'}, status=404)
    code = data.get('code', '')
    if not isinstance(code, str) or len(code) > 20000:
        return JsonResponse({'error': 'Code is too long.'}, status=400)
    visible_tests = list(task.test_cases.filter(is_hidden=False).order_by('id'))
    results = []
    passed = 0
    for case_no, test in enumerate(visible_tests, 1):
        output, error = run_code(code, test.input_data, task.language)
        ok = not error and output == test.expected_output.strip()
        passed += int(ok)
        results.append({
            'case': case_no,
            'verdict': 'Accepted' if ok else ('Runtime Error' if error else 'Wrong Answer'),
            'ok': ok,
        })
    ExamEvent.objects.create(student=request.user, exam=exam, kind='run', task_number=task_number(exam, task), passed=passed, total=len(visible_tests))
    return JsonResponse({'results': results, 'passed': passed, 'total': len(visible_tests)})

@login_required
@require_POST
def submit_task_view(request, exam_id):
    if request.user.role != 'student':
        return JsonResponse({'error': 'You are not allowed to do this.'}, status=403)

    exam = get_object_or_404(
        Exam,
        id=exam_id,
        exam_type='code',
        groups__students=request.user,
    )

    if ExamResult.objects.filter(student=request.user, exam=exam).exists() \
            or not exam.is_open(grace_seconds=30):
        return JsonResponse({'error': 'This exam is closed.'}, status=403)

    try:
        data = json.loads(request.body)
        task = CodeTask.objects.filter(id=int(data.get('task_id')), exam=exam).first()
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid request.'}, status=400)

    if task is None:
        return JsonResponse({'error': 'Task not found.'}, status=404)

    code = data.get('code', '')
    if len(code) > 20000:
        return JsonResponse({'error': 'Code is too long.'}, status=400)

    passed, count = check_task(task, code)
    earned = task.points * passed / count if count else 0.0

    CodeSubmissionAttempt.objects.create(student=request.user, task=task, code=code, passed=passed, total=count, score=earned)
    CodeSubmission.objects.update_or_create(
        student=request.user, task=task,
        defaults={'code': code, 'passed': passed, 'total': count, 'score': earned},
    )
    ExamEvent.objects.create(
    student=request.user, exam=exam, kind='submit_task',
    task_number=task_number(exam, task), passed=passed, total=count,
    score=earned, max_score=task.points,
    )
    return JsonResponse({'task_id': task.id, 'accepted': bool(count and passed == count), 'score': round(earned, 2), 'max': task.points})

@login_required
@require_POST
def reset_result_view(request, exam_id, student_id):
    if not request.user.is_teacher():
        return redirect('dashboard')

    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    student = get_object_or_404(User, id=student_id)

    with transaction.atomic():
        ExamResult.objects.filter(student=student, exam=exam).delete()
        ExamSession.objects.filter(student=student, exam=exam).delete()
        Answer.objects.filter(student=student, question__exam=exam).delete()
        CodeSubmission.objects.filter(student=student, task__exam=exam).delete()
        CodeSubmissionAttempt.objects.filter(student=student, task__exam=exam).delete()
        Violation.objects.filter(student=student, exam=exam).delete()
        ExamEvent.objects.filter(student=student, exam=exam).delete()

    messages.success(
        request,
        f"{student.get_full_name() or student.username} exam result was reset.",
    )
    return redirect('exam_results', exam_id=exam.id)

@login_required
def admin_users_view(request):
    if not request.user.is_admin() or request.user.institution is None:
        return redirect('dashboard')

    institution = request.user.institution

    teachers = (
        User.objects.filter(institution=institution, role='teacher')
        .prefetch_related('teacher_groups')
        .order_by('last_name', 'first_name', 'username')
    )
    groups = (
        Group.objects.filter(institution=institution)
        .select_related('teacher')
        .annotate(student_count=Count('students'))
        .order_by('name')
    )
    no_group_count = User.objects.filter(
        institution=institution, role='student', student_groups__isnull=True
    ).count()

    return render(request, 'admin_users.html', {
        'teachers': teachers,
        'groups': groups,
        'no_group_count': no_group_count,
    })


@login_required
def admin_group_detail_view(request, group_id):
    if not request.user.is_admin() or request.user.institution is None:
        return redirect('dashboard')

    group = get_object_or_404(
        Group.objects.select_related('teacher'),
        id=group_id, institution=request.user.institution,
    )

    if request.method == 'POST':
        student = group.students.filter(id=request.POST.get('student_id')).first()
        if student:
            group.students.remove(student)
            messages.success(
                request,
                f"{student.get_full_name() or student.username} was removed from the group.",
            )
        return redirect('admin_group_detail', group_id=group.id)

    students = group.students.order_by('last_name', 'first_name', 'username')
    return render(request, 'admin_group_detail.html', {
        'group': group,
        'students': students,
    })

VIOLATION_KINDS = {'tab_hidden', 'window_blur', 'paste'}


@login_required
@require_POST
def exam_violation_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.user.role != 'student' \
            or ExamResult.objects.filter(student=request.user, exam=exam).exists() \
            or not exam.is_open(grace_seconds=30):
        return JsonResponse({'ignored': True})

    try:
        kind = json.loads(request.body).get('kind')
    except ValueError:
        return JsonResponse({'error': 'Invalid request.'}, status=400)
    if kind not in VIOLATION_KINDS:
        return JsonResponse({'error': 'Invalid event type.'}, status=400)

    # 3 saniyə ərzində təkrarlananları (blur + tab dəyişmə eyni anda) bir say
    last = Violation.objects.filter(student=request.user, exam=exam).order_by('-created_at').first()
    if last is None or (timezone.now() - last.created_at).total_seconds() >= 1:
        Violation.objects.create(student=request.user, exam=exam, kind=kind)

    count = Violation.objects.filter(student=request.user, exam=exam).count()
    limit = getattr(exam, 'max_warnings', 3) or 3
    return JsonResponse({'count': count, 'max': limit, 'removed': count >= limit})

KIND_LABELS = {
    'tab_hidden': 'Switched to another tab',
    'window_blur': 'Left the exam window',
    'paste': 'Pasted text',
}


@login_required
def teacher_live_view(request):
    if not request.user.is_teacher():
        return redirect('dashboard')
    return render(request, 'teacher_live.html')


@login_required
def teacher_live_feed_view(request):
    if not request.user.is_teacher():
        return JsonResponse({'error': 'forbidden'}, status=403)

    me = request.user
    now = timezone.now()
    since = parse_datetime(request.GET.get('since', '') or '') or (now - timedelta(hours=3))
    if timezone.is_naive(since):
        since = timezone.make_aware(since)

    def name(u):
        return u.get_full_name() or u.username

    events = []
    for s in ExamSession.objects.filter(
            exam__created_by=me, started_at__gt=since).select_related('student', 'exam'):
        events.append({'t': s.started_at, 'kind': 'entered', 'student': name(s.student),
                       'exam': s.exam.title, 'detail': 'Started the exam'})

    for v in Violation.objects.filter(
            exam__created_by=me, created_at__gt=since).select_related('student', 'exam'):
        events.append({'t': v.created_at, 'kind': 'warning', 'student': name(v.student),
                       'exam': v.exam.title, 'detail': KIND_LABELS.get(v.kind, v.kind)})

    for r in ExamResult.objects.filter(
            exam__created_by=me, submitted_at__gt=since).select_related('student', 'exam'):
        events.append({'t': r.submitted_at, 'kind': 'submitted', 'student': name(r.student),
                       'exam': r.exam.title, 'detail': f'Finished the exam ({r.score:g} / {r.total:g})'})

    for ev in ExamEvent.objects.filter(
            exam__created_by=me, created_at__gt=since).select_related('student', 'exam'):
        if ev.kind == 'run':
            kind = 'run'
            detail = f'Task {ev.task_number}: ran code ({ev.passed}/{ev.total} public tests passed)'
        else:
            kind = 'task'
            detail = (f'Task {ev.task_number}: submitted code, {ev.passed}/{ev.total} tests passed, '
                      f'{ev.score:g}/{ev.max_score:g} points')
        events.append({'t': ev.created_at, 'kind': kind, 'student': name(ev.student),
                       'exam': ev.exam.title, 'detail': detail})

    events.sort(key=lambda e: e['t'])
    for e in events:
        e['t'] = e['t'].isoformat()

    # Hazırda imtahan verənlər
    finished = set(ExamResult.objects.filter(exam__created_by=me)
                   .values_list('student_id', 'exam_id'))
    warn_counts = {
        (st, ex): c
        for st, ex, c in Violation.objects.filter(exam__created_by=me)
        .values_list('student_id', 'exam_id').annotate(c=Count('id'))
    }
    active = []
    for s in ExamSession.objects.filter(
            exam__created_by=me, last_seen_at__gte=now - timedelta(seconds=45)
    ).select_related('student', 'exam'):
        key = (s.student_id, s.exam_id)
        if key in finished or not s.exam.is_open(grace_seconds=30):
            continue
        active.append({
            'student': name(s.student), 'exam': s.exam.title,
            'warnings': warn_counts.get(key, 0),
            'max': getattr(s.exam, 'max_warnings', 3) or 3,
            'last_seen': s.last_seen_at.isoformat(),
        })
    active.sort(key=lambda a: -a['warnings'])

    return JsonResponse({'now': now.isoformat(), 'events': events, 'active': active})

def task_number(exam, task):
    ids = list(exam.code_tasks.order_by('id').values_list('id', flat=True))
    return ids.index(task.id) + 1
