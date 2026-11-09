from django.db import models
from django.conf import settings
from .question import Question
from datetime import timedelta
from django.utils import timezone

class Exam(models.Model):
    EXAM_TYPES = [
        ('test', 'Test'),
        ('written', 'Written'),
        ('code', 'Programming (Code)'),
    ]
    title = models.CharField(max_length=200, verbose_name="Exam title")
    exam_type = models.CharField(
        max_length=10,
        choices=EXAM_TYPES,
        default='test',
        verbose_name="Exam type"
    )
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    duration_minutes = models.IntegerField(default=60, verbose_name="Duration (minutes)")
    max_warnings = models.IntegerField(default=3, verbose_name="Maximum warning limit")
    questions_per_student = models.PositiveIntegerField(default=10, verbose_name="Questions per student")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="Start time")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="End time")
    groups = models.ManyToManyField('core.Group', related_name='exams', blank=True, verbose_name="Groups")
    created_at = models.DateTimeField(auto_now_add=True)
    allow_reentry = models.BooleanField(default=True, verbose_name="Allow re-entry")
    def scheduled_end_time(self):
        if self.end_time:
            return self.end_time

    # Köhnə imtahanlarda end_time boşdursa, əvvəlki qayda işləsin
        if self.start_time:
            return self.start_time + timedelta(minutes=self.duration_minutes)

        return None

    def is_open(self, grace_seconds=0):
        if not self.start_time:
            return True

        end_time = self.scheduled_end_time()
        if not end_time:
            return True

        now = timezone.now()
        return self.start_time <= now < end_time + timedelta(seconds=grace_seconds)

    def remaining_seconds(self):
        end_time = self.scheduled_end_time()

        if not self.start_time or not end_time:
            return self.duration_minutes * 60

        return max(0, int((end_time - timezone.now()).total_seconds()))

    def has_ended(self):
        if not self.start_time:
            return False

        end_time = self.scheduled_end_time()
        return bool(end_time and timezone.now() >= end_time)

class Ticket(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='tickets')
    name = models.CharField(max_length=50, verbose_name="Ticket name (e.g. Ticket 1)")
    questions = models.ManyToManyField(Question, related_name='tickets')

    def __str__(self):
        return f"{self.exam.title} - {self.name}"