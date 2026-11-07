from django.conf import settings
from django.db import models


class ExamEvent(models.Model):
    KINDS = (('run', 'Nümunə yoxlama'), ('submit_task', 'Tapşırıq təhvili'))

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exam_events"
    )
    exam = models.ForeignKey("core.Exam", on_delete=models.CASCADE, related_name="events")
    kind = models.CharField(max_length=20, choices=KINDS)
    task_number = models.IntegerField(default=0)
    passed = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    score = models.FloatField(default=0.0)
    max_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]