from django.conf import settings
from django.db import models


class ExamResult(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_results",
        verbose_name="Tələbə",
    )
    exam = models.ForeignKey(
        "core.Exam",
        on_delete=models.CASCADE,
        related_name="results",
        verbose_name="İmtahan",
    )
    score = models.IntegerField(verbose_name="Düzgün cavab sayı")
    total = models.IntegerField(verbose_name="Ümumi sual sayı")
    submitted_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Təhvil verilmə tarixi"
    )

    class Meta:
        
        unique_together = ("student", "exam")
        verbose_name = "İmtahan Nəticəsi"
        verbose_name_plural = "İmtahan Nəticələri"