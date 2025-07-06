from django.db import models

# Student Table
class Student(models.Model):
    reg_no = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    student_class = models.CharField(max_length=50)
    year = models.IntegerField()

    def __str__(self):
        return self.name

# Attendance Table
class Attendance(models.Model):
    reg_no = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    subject = models.CharField(max_length=100)
    mode = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    def __str__(self):
        return f"{self.reg_no} - {self.subject} - {self.date}"

# Exam Table
class Exam(models.Model):
    EXAM_TYPE_CHOICES = [
        ('Test', 'Test'),
        ('Semester', 'Semester'),
    ]

    reg_no = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPE_CHOICES)
    date = models.DateField()
    marks = models.IntegerField()

    def __str__(self):
        return f"{self.reg_no} - {self.subject} - {self.exam_type}"
