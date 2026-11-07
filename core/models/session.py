from django.conf import settings
from django.db import models


class ExamSession(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_sessions",
        verbose_name="Tələbə",
    )
    exam = models.ForeignKey(
        "core.Exam",
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="İmtahan",
    )
    questions = models.ManyToManyField(
        "core.Question",
        related_name="sessions",
        verbose_name="Təyin olunmuş suallar",
    )
    started_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Başlama tarixi"
    )

    class Meta:
        unique_together = ("student", "exam")
        verbose_name = "İmtahan Sessiyası"
        verbose_name_plural = "İmtahan Sessiyaları"

    def __str__(self):
        return f"{self.student.username} - {self.exam.title} Sessiyası"