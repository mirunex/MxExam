from django.conf import settings
from django.db import models


class ExamSession(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_sessions",
        verbose_name="Student",
    )
    exam = models.ForeignKey(
        "core.Exam",
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="Exam",
    )
    questions = models.ManyToManyField(
        "core.Question",
        related_name="sessions",
        verbose_name="Assigned questions",
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Start time")
    last_seen_at = models.DateTimeField(null=True, blank=True, verbose_name="Last activity")

    class Meta:
        unique_together = ("student", "exam")
        verbose_name = "Exam session"
        verbose_name_plural = "Exam sessions"

    def __str__(self):
        return f"{self.student.username} - {self.exam.title} session"