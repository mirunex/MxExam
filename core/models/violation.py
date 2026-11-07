from django.conf import settings
from django.db import models


class Violation(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="violations"
    )
    exam = models.ForeignKey("core.Exam", on_delete=models.CASCADE, related_name="violations")
    kind = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.student} - {self.exam} - {self.kind}"