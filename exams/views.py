from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Exam
from .forms import QuestionForm, ExamForm  # Əgər ExamForm istifadə edirsinizsə


@login_required
def teacher_dashboard(request):
    # 1. Müəllim statusunu təhlükəsiz yoxlayırıq (həm field, həm metod kimi)
    is_teacher_user = getattr(request.user, 'is_teacher', False)
    if callable(is_teacher_user):
        is_teacher_user = is_teacher_user()

    if not is_teacher_user:
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            return redirect('teacher_dashboard')
        else:
            print("FORM XƏTASI:", form.errors)
    else:
        form = ExamForm()

    exams = Exam.objects.filter(created_by=request.user)
    return render(request, 'teacher_dashboard.html', {
        'form': form,
        'exams': exams
    })


@login_required
def student_dashboard(request):
    exams = Exam.objects.all()
    return render(request, 'student_dashboard.html', {'exams': exams})


@login_required
def delete_exam_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    if request.method == 'POST':
        exam.delete()
    return redirect('teacher_dashboard')