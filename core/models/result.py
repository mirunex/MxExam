from django.conf import settings
from django.db import models


class ExamResult(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_results",
        verbose_name="Student",
    )
    exam = models.ForeignKey(
        "core.Exam",
        on_delete=models.CASCADE,
        related_name="results",
        verbose_name="Exam",
    )
    score = models.IntegerField(verbose_name="Score")
    total = models.IntegerField(verbose_name="Total")
    submitted_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Submitted at"
    )

    class Meta:
        
        unique_together = ("student", "exam")
        verbose_name = "Exam result"
        verbose_name_plural = "Exam results"