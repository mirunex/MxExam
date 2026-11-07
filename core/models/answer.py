from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Answer(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers', verbose_name="Tələbə")
    question = models.ForeignKey('core.Question', on_delete=models.CASCADE, related_name='answers', verbose_name="Sual")

    # Test sualı üçün
    selected_option = models.CharField(max_length=1, blank=True, default="", verbose_name="Seçilmiş variant")

    # Yazılı sual üçün
    text_answer = models.TextField(blank=True, default="", verbose_name="Yazılı cavab")
    awarded_points = models.FloatField(null=True, blank=True, verbose_name="Verilən bal")
    # None = müəllim hələ yoxlamayıb

    class Meta:
        unique_together = ('student', 'question')

    def is_correct(self):
        if not self.question.correct_option:
            return False
        return self.selected_option.strip().upper() == self.question.correct_option.strip().upper()

    def is_graded(self):
        return self.awarded_points is not None