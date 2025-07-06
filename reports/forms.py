from django import forms
from .models import Student, Attendance, Exam
from django.contrib.auth.models import User



class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Hash the password
        if commit:
            user.save()
        return user

# Student Form
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['reg_no', 'name', 'branch', 'student_class', 'year']

# Attendance Form
class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['reg_no', 'date', 'subject', 'mode']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

# Exam Form
class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['reg_no', 'subject', 'exam_type', 'date', 'marks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
