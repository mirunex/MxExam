from django import forms
from core.models.exam import Exam

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'description', 'duration_minutes', 'max_warnings']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'İmtahan adı',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'İmtahan haqqında ətraflı...'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Məsələn: 60',
                'min': '1',
                'required': 'required'
            }),
            'max_warnings': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Məsələn: 3',
                'min': '0',
                'required': 'required'
            }),
        }

    def clean_duration_minutes(self):
        duration = self.cleaned_data.get('duration_minutes')
        if duration is not None and duration < 1:
            raise forms.ValidationError("İmtahan müddəti ən azı 1 dəqiqə olmalıdır.")
        return duration

    def clean_max_warnings(self):
        warnings = self.cleaned_data.get('max_warnings')
        if warnings is not None and warnings < 0:
            raise forms.ValidationError("Xəbərdarlıq limiti mənfi ola bilməz.")
        return warnings