from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models.user import User
from .models.question import Question
from .models.exam import Exam, Ticket
from .models import Group, Exam 

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Rol Məlumatı', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Rol Məlumatı', {'fields': ('role',)}),
    )

# Yeni modellərin qeydiyyatı
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question_type', 'points')
    list_filter = ('question_type',)

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'duration_minutes', 'max_warnings')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam')


admin.site.register(Group)