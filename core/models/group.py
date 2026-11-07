from django.conf import settings
from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=50)

    institution = models.ForeignKey(
        'core.Institution',
        on_delete=models.PROTECT,
        related_name='groups',
        null=True,
        blank=True,
        verbose_name='Müəssisə',
    )

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='teacher_groups'
    )
    
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'student'},
        related_name='student_groups',
        blank=True
    )

    def __str__(self):
        return self.name