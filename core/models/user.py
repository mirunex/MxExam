from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=[("student", "Tələbə"), ("teacher", "Müəllim"), ("admin", "Admin"), ("superadmin", "Super Admin")],
        default="student",
    )
    institution = models.ForeignKey(
    "core.Institution",
    on_delete=models.PROTECT,
    null=True,
    blank=True,
    related_name="users",
    verbose_name="Müəssisə",
)
    def is_teacher(self):
        return self.role == 'teacher'
    def is_admin(self):
        return self.role == 'admin'
    def is_superadmin(self):
        return self.role == 'superadmin'
    