from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Question(models.Model):
    QUESTION_TYPES = (
        ('test', 'Test (A-D)'),
        ('written', 'Yazılı'),
        ('code', 'Proqramlaşdırma (Kod)'),
    )
    
    text = models.TextField(verbose_name="Sualın mətni")
    points = models.FloatField(default=1.0, verbose_name="Sualın maks balı")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='test')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='questions')
    exam = models.ForeignKey('core.Exam', on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
  
    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)
    correct_option = models.CharField(max_length=1, blank=True, null=True, help_text="A, B, C və ya D")

    def __str__(self):
        return f"[{self.get_question_type_display()}] {self.text[:30]}..."

    def calculate_score(self, student_answer):
        """
        Qismən bal məntiqi:
        Test sualı üçün tam bal (0 və ya 1).
        Yazılı sual üçün avtomatik yoxlanmır (None qaytarır, müəllim yoxlayır).
        """
        if self.question_type == 'test':
            if student_answer and self.correct_option and student_answer.strip().upper() == self.correct_option.strip().upper():
                return self.points
            return 0.0
        elif self.question_type == 'written':
            return None  
        return 0.0
    def clean(self):
        super().clean()
        if self.question_type == 'test':
            options = [self.option_a, self.option_b, self.option_c, self.option_d]
            if not all(options):
                raise ValidationError("Test tipli suallar üçün bütün variantlar (A, B, C, D) doldurulmalıdır.")
            if not self.correct_option or self.correct_option.strip().upper() not in ['A', 'B', 'C', 'D']:
                raise ValidationError("Düzgün cavab yalnız A, B, C və ya D ola bilər.")
