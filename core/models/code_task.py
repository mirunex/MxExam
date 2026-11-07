from django.db import models
from django.conf import settings


class CodeTask(models.Model):
    LANGUAGES = [('python', 'Python'), ('java', 'Java')]

    exam = models.ForeignKey(
        "core.Exam", on_delete=models.CASCADE, related_name="code_tasks"
    )
    language = models.CharField(
        max_length=10, choices=LANGUAGES, default='python', verbose_name="Dil"
    )
    title = models.CharField(max_length=150, verbose_name="Başlıq")
    title_en = models.CharField(max_length=150, blank=True, verbose_name="Başlıq (en)")
    title_ru = models.CharField(max_length=150, blank=True, verbose_name="Başlıq (ru)")
    description = models.TextField(verbose_name="Tapşırığın mətni")
    description_en = models.TextField(blank=True, verbose_name="Tapşırığın mətni (en)")
    description_ru = models.TextField(blank=True, verbose_name="Tapşırığın mətni (ru)")
    starter_code = models.TextField(blank=True, verbose_name="Başlanğıc kod")
    reference_code = models.TextField(blank=True, verbose_name="Etalon kod (müəllimin həlli)")
    points = models.FloatField(default=10.0, verbose_name="Maks bal")

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
    input_data = models.TextField(blank=True, verbose_name="Giriş")
    expected_output = models.TextField(verbose_name="Gözlənilən çıxış")
    is_hidden = models.BooleanField(default=False, verbose_name="Gizli test")

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