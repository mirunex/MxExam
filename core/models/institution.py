from django.db import models
from django.utils.text import slugify

class Institution(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Müəssisə adı",
    )
    slug = models.SlugField(
        max_length=80,
        unique=True,
        null=True,
        blank=True,
        editable=False,
        verbose_name='Qısa kod',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaradılma tarixi",
    )

    class Meta:
        verbose_name = "Müəssisə"
        verbose_name_plural = "Müəssisələr"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or 'institution'
            candidate = base_slug
            number = 2

            while Institution.objects.exclude(pk=self.pk).filter(
                slug=candidate
            ).exists():
                candidate = f'{base_slug}-{number}'
                number += 1

            self.slug = candidate

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def admins(self):
        return self.users.filter(role='admin')