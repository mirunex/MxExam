from django.db import models
from django.conf import settings


class CodeTask(models.Model):
    LANGUAGES = [('python', 'Python'), ('java', 'Java')]

    exam = models.ForeignKey(
        "core.Exam", on_delete=models.CASCADE, related_name="code_tasks"
    )
    language = models.CharField(
        max_length=10, choices=LANGUAGES, default='python', verbose_name="Language"
    )
    title = models.CharField(max_length=150, verbose_name="Title")
    title_en = models.CharField(max_length=150, blank=True, verbose_name="Title (English)")
    title_ru = models.CharField(max_length=150, blank=True, verbose_name="Title (Russian)")
    description = models.TextField(verbose_name="Task description")
    description_en = models.TextField(blank=True, verbose_name="Task description (English)")
    description_ru = models.TextField(blank=True, verbose_name="Task description (Russian)")
    starter_code = models.TextField(blank=True, verbose_name="Starter code")
    reference_code = models.TextField(blank=True, verbose_name="Reference solution")
    points = models.FloatField(default=10.0, verbose_name="Maximum score")

    def __str__(self):
        return self.title

    def visible_tests(self):
        return self.test_cases.filter(is_hidden=False)

    def get_title(self, lang='az'):
        return (getattr(self, f'title_{lang}', '') if lang in ('en', 'ru') else '') or self.title

    def get_description(self, lang='az'):
        return (getattr(self, f'description_{lang}', '') if lang in ('en', 'ru') else '') or self.description


class CodeTestCase(models.Model):
    task = models.ForeignKey(
        CodeTask, on_delete=models.CASCADE, related_name="test_cases"
    )
    input_data = models.TextField(blank=True, verbose_name="Input")
    expected_output = models.TextField(verbose_name="Expected output")
    is_hidden = models.BooleanField(default=False, verbose_name="Hidden test")

    def __str__(self):
        return f"{self.task.title} testi"


class CodeSubmission(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="code_submissions"
    )
    task = models.ForeignKey(CodeTask, on_delete=models.CASCADE, related_name="submissions")
    code = models.TextField(blank=True)
    passed = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    score = models.FloatField(default=0.0)

    class Meta:
        unique_together = ("student", "task")

class CodeSubmissionAttempt(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="code_submission_attempts")
    task = models.ForeignKey(CodeTask, on_delete=models.CASCADE, related_name="submission_attempts")
    code = models.TextField(blank=True)
    passed = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    score = models.FloatField(default=0.0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["submitted_at"]
        verbose_name = "Code submission attempt"
        verbose_name_plural = "Code submission attempts"
