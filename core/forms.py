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
                    'placeholder': 'Institution name',
                }
            ),
        }
        labels = {
            'name': 'Institution name',
        }
        error_messages = {
            'name': {
            'unique': 'An institution with this name already exists.',
        }
}

User = get_user_model()

class InstitutionAdminForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password',
            }
        ),
        label='Password',
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Username'}
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
                    'placeholder': 'Email address',
                }
            ),
        }
        labels = {
            'username': 'Username',
            'first_name': 'Ad',
            'last_name': 'Soyad',
            'email': 'Email',
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
                'placeholder': 'Password',
            }
        ),
        label='Password',
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Username'}
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
                    'placeholder': 'Email address',
                }
            ),
        }
        labels = {
            'username': 'Username',
            'first_name': 'Ad',
            'last_name': 'Soyad',
            'email': 'Email',
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
    start_time = forms.DateTimeField(
    required=True,
    input_formats=["%Y-%m-%dT%H:%M"],
    widget=forms.DateTimeInput(
        attrs={"class": "form-control", "type": "text", "autocomplete": "off"},
        format="%Y-%m-%dT%H:%M",
    ),
)

    end_time = forms.DateTimeField(
    required=True,
    input_formats=["%Y-%m-%dT%H:%M"],
    widget=forms.DateTimeInput(
        attrs={"class": "form-control", "type": "text", "autocomplete": "off"},
        format="%Y-%m-%dT%H:%M",
    ),
)
    class Meta:
        model = Exam
        fields = [
    'title',
    'description',
    'max_warnings',
    'questions_per_student',
    'start_time',
    'end_time',
    'groups',
    'exam_type',
    'allow_reentry',
]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Exam title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'max_warnings': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Maximum warning count'}),
            'questions_per_student': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(
    attrs={'class': 'form-control', 'type': 'text', 'autocomplete': 'off'},
    format='%Y-%m-%dT%H:%M',
),
            'end_time': forms.DateTimeInput(
    attrs={'class': 'form-control', 'type': 'text', 'autocomplete': 'off'},
    format='%Y-%m-%dT%H:%M',
),
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
            raise forms.ValidationError("Exam duration must be greater than zero.")
        return duration
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and end_time <= start_time:
            self.add_error('end_time', 'The end time must be later than the start time.')

        return cleaned_data
    def clean_max_warnings(self):
        warnings = self.cleaned_data.get('max_warnings')
        if warnings is not None and warnings < 0:
            raise forms.ValidationError("Warning count cannot be negative.")
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
            'correct_option': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A, B, C, or D'}),
            

        }

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Example: 2445a'}),
        }

class AdminGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'teacher']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Example: 2445a',
                }
            ),
            'teacher': forms.Select(
                attrs={'class': 'form-control'}
            ),
        }
        labels = {
            'name': 'Group name',
            'teacher': 'Teacher',
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
        label="Question file (PDF or Excel)",
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf,.xlsx'}),
    )

    def clean_pdf_file(self):
        file = self.cleaned_data["pdf_file"]
        name = file.name.lower()

        if not (name.endswith(".pdf") or name.endswith(".xlsx")):
            raise ValidationError("Only PDF or Excel (.xlsx) files are allowed.")

        if file.size > 10 * 1024 * 1024:
            raise ValidationError("The file must not exceed 10 MB.")

        return file
