from django import forms
from core.models import Question, Exam, Group
from django.core.exceptions import ValidationError
from core.models.institution import Institution
from django.contrib.auth import get_user_model

class InstitutionForm(forms.ModelForm):

    class Meta:
        model = Institution
        fields = ['name']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Müəssisənin adı',
                }
            ),
        }
        labels = {
            'name': 'Müəssisə adı',
        }
        error_messages = {
            'name': {
            'unique': 'Bu adla müəssisə artıq mövcuddur.',
        }
}

User = get_user_model()

class InstitutionAdminForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Şifrə',
            }
        ),
        label='Şifrə',
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'İstifadəçi adı'}
            ),
            'first_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ad'}
            ),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Soyad'}
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'E-poçt ünvanı',
                }
            ),
        }
        labels = {
            'username': 'İstifadəçi adı',
            'first_name': 'Ad',
            'last_name': 'Soyad',
            'email': 'E-poçt',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
class TeacherForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Şifrə',
            }
        ),
        label='Şifrə',
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'İstifadəçi adı'}
            ),
            'first_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ad'}
            ),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Soyad'}
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'E-poçt ünvanı',
                }
            ),
        }
        labels = {
            'username': 'İstifadəçi adı',
            'first_name': 'Ad',
            'last_name': 'Soyad',
            'email': 'E-poçt',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
class StudentForm(TeacherForm):
    pass
class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = [
            'title', 
            'description', 
            'duration_minutes', 
            'max_warnings', 
            'questions_per_student', 
            'start_time', 
            'groups',
            'exam_type',
            'allow_reentry',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'İmtahan Adı'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Açıqlama'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Müddət (dəqiqə)'}),
            'max_warnings': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Maksimum xəbərdarlıq sayı'}),
            'questions_per_student': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'groups': forms.CheckboxSelectMultiple(),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
        }
    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['groups'].queryset = Group.objects.filter(
                institution=teacher.institution
            ).order_by('name')
    def clean_duration_minutes(self):
        duration = self.cleaned_data.get('duration_minutes')
        if duration is not None and duration <= 0:
            raise forms.ValidationError("İmtahan müddəti 0-dan böyük olmalıdır.")
        return duration

    def clean_max_warnings(self):
        warnings = self.cleaned_data.get('max_warnings')
        if warnings is not None and warnings < 0:
            raise forms.ValidationError("Xəbərdarlıq sayı mənfi ola bilməz.")
        return warnings


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'points', 'question_type', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'points': forms.NumberInput(attrs={'class': 'form-control'}),
            'question_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_question_type'}),
            'option_a': forms.TextInput(attrs={'class': 'form-control'}),
            'option_b': forms.TextInput(attrs={'class': 'form-control'}),
            'option_c': forms.TextInput(attrs={'class': 'form-control'}),
            'option_d': forms.TextInput(attrs={'class': 'form-control'}),
            'correct_option': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A, B, C və ya D'}),
            

        }

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Məs: 2445a'}),
        }

class AdminGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'teacher']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Məs: 2445a',
                }
            ),
            'teacher': forms.Select(
                attrs={'class': 'form-control'}
            ),
        }
        labels = {
            'name': 'Qrupun adı',
            'teacher': 'Müəllim',
        }

    def __init__(self, *args, institution=None, **kwargs):
        super().__init__(*args, **kwargs)

        if institution:
            self.fields['teacher'].queryset = User.objects.filter(
                institution=institution,
                role='teacher',
            ).order_by('first_name', 'last_name', 'username')

class PDFUploadForm(forms.Form):
    pdf_file = forms.FileField(
        label="Sual faylı (PDF və ya Excel)",
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf,.xlsx'}),
    )

    def clean_pdf_file(self):
        file = self.cleaned_data["pdf_file"]
        name = file.name.lower()

        if not (name.endswith(".pdf") or name.endswith(".xlsx")):
            raise ValidationError("Yalnız PDF və ya Excel (.xlsx) faylı yükləmək olar.")

        if file.size > 10 * 1024 * 1024:
            raise ValidationError("Fayl 10 MB-dan böyük olmamalıdır.")

        return file