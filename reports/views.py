from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, Attendance, Exam
from .forms import StudentForm, AttendanceForm, ExamForm, UserRegistrationForm
from django.contrib.auth import login, authenticate, logout

from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse

# Home Page
def home(request):
    return render(request, 'reports/home.html')
@login_required
def edit_student(request, reg_no):
    student = get_object_or_404(Student, reg_no=reg_no)

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')  # Redirect to student list after editing
    else:
        form = StudentForm(instance=student)

    return render(request, 'reports/edit_student.html', {'form': form, 'student': student})
# Student List with Form
def student_list(request):
    students = Student.objects.all()
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'reports/student_list.html', {'students': students, 'form': form})
@login_required
def delete_student(request, reg_no):
    student = get_object_or_404(Student, reg_no=reg_no)
    if request.method == "POST":
        student.delete()
        return redirect('student_list')

    return render(request, 'reports/delete_student.html', {'student': student})

# Attendance Report with Form
@login_required
def attendance_report(request):
    form = AttendanceForm(request.POST or None)
    attendance_records = Attendance.objects.all()

    if request.method == "POST" and 'filter_date' in request.POST:
        date_filter = request.POST.get("date_filter")
        if date_filter:
            attendance_records = attendance_records.filter(date=date_filter)

    if request.method == "POST" and form.is_valid():
        form.save()

    return render(request, 'reports/attendance_report.html', {
        'form': form,
        'attendance_records': attendance_records,
    })

@login_required
def edit_attendance(request, attendance_id):
    attendance = get_object_or_404(Attendance, id=attendance_id)

    if request.method == "POST":
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            return redirect('attendance_report')  # Redirect to attendance report after editing
    else:
        form = AttendanceForm(instance=attendance)

    return render(request, 'reports/edit_attendance.html', {'form': form, 'attendance': attendance})

@login_required
def delete_attendance(request, attendance_id):
    attendance = get_object_or_404(Attendance, id=attendance_id)
    if request.method == "POST":
        attendance.delete()
        return redirect('attendance_report')

    return render(request, 'reports/delete_attendance.html', {'attendance': attendance})

# Exam Report with Form
@login_required
def exam_report(request):
    form = ExamForm(request.POST or None)
    exam_records = Exam.objects.all()

    if request.method == "POST" and 'filter_exam' in request.POST:
        exam_filter = request.POST.get("exam_filter")
        if exam_filter:
            exam_records = exam_records.filter(exam_type=exam_filter)

    if request.method == "POST" and form.is_valid():
        form.save()

    return render(request, 'reports/exam_report.html', {
        'form': form,
        'exam_records': exam_records,
    })

@login_required
def topper_report(request):
    query = request.GET.get('q', '')

    # Annotate total marks from Exam model
    toppers = Student.objects.annotate(
        total_marks=Sum('exam__marks')
    ).order_by('-total_marks')

    # Apply search filter if query exists
    if query:
        toppers = toppers.filter(name__icontains=query) | toppers.filter(reg_no__icontains=query)

    return render(request, 'reports/topper_report.html', {'toppers': toppers, 'query': query})


@login_required
def defaulter_report(request):
    year_filter = request.GET.get("year")
    defaulters = Student.objects.all()

    if year_filter:
        defaulters = defaulters.filter(year=year_filter)

    defaulters = defaulters.annotate(total_marks=Sum('exam__marks')).filter(total_marks__lt=40)

    return render(request, 'reports/defaulter_report.html', {
        'defaulters': defaulters,
        'year_filter': year_filter
    })


#PDF report


def generate_pdf_report(title, headers, data):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{title}.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, title)

    p.setFont("Helvetica", 12)
    
    x_offset = 50
    y_offset = height - 100

    for header in headers:
        p.drawString(x_offset, y_offset, header)
        x_offset += 150

    y_offset -= 20
    p.line(50, y_offset, width - 50, y_offset)
    y_offset -= 20

    for row in data:
        x_offset = 50
        for col in row:
            p.drawString(x_offset, y_offset, str(col))
            x_offset += 150
        y_offset -= 20

    p.showPage()
    p.save()
    
    return response

@login_required
def attendance_pdf(request):
    attendance_records = Attendance.objects.all().values_list(
        'reg_no__reg_no', 'date', 'subject', 'mode'
    )
    
    return generate_pdf_report(
        "Attendance Report",
        ["Reg No", "Date", "Subject", "Status"],
        attendance_records
    )

@login_required
def topper_pdf(request):
    toppers = Student.objects.annotate(total_marks=Sum('exam__marks')).order_by('-total_marks')[:5]
    data = [(t.reg_no, t.name, t.total_marks) for t in toppers]

    return generate_pdf_report(
        "Topper Report",
        ["Reg No", "Name", "Total Marks"],
        data
    )

@login_required
def defaulter_pdf(request):
    defaulters = Student.objects.annotate(total_marks=Sum('exam__marks')).filter(total_marks__lt=40)
    data = [(d.reg_no, d.name, d.total_marks) for d in defaulters]

    return generate_pdf_report(
        "Defaulter Report",
        ["Reg No", "Name", "Total Marks"],
        data
    )

from django.conf import settings
import os

def register(request):
    # Debugging: Print template path
    template_path = os.path.join(settings.BASE_DIR, 'student_report', 'reports', 'templates', 'reports', 'register.html')

    if not os.path.exists(template_path):
        print(f"❌ Template not found at: {template_path}")
    else:
        print(f"✅ Template exists at: {template_path}")

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')





def graphical_report(request):
    students = Student.objects.all()
    student_names = []
    attendance_percentages = []
    total_marks_list = []

    for student in students:
        # Fetch total classes attended
        total_classes = Attendance.objects.filter(reg_no=student).count()
        attended_classes = Attendance.objects.filter(reg_no=student, mode='Present').count()

        # Avoid division by zero
        if total_classes > 0:
            attendance_percentage = (attended_classes / total_classes) * 100
        else:
            attendance_percentage = 0  # No records, assume 0%

        # Fetch total marks for all exams
        total_marks = Exam.objects.filter(reg_no=student).aggregate(total=Sum('marks'))['total'] or 0


        # Append to lists
        student_names.append(student.name)
        attendance_percentages.append(round(attendance_percentage, 2))  # Round to 2 decimal places
        total_marks_list.append(total_marks)

    context = {
        "student_names": json.dumps(student_names),
        "attendance": json.dumps(attendance_percentages),
        "marks": json.dumps(total_marks_list),
    }
    return render(request, "reports/graphical_report.html", context)

#EXAM



# View to display all exams
def exam_list(request):
    exams = Exam.objects.all()
    return render(request, 'reports/exam_list.html', {'exams': exams})

# View to add an exam
def add_exam(request):
    if request.method == "POST":
        form = ExamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('exam_list')
    else:
        form = ExamForm()
    
    return render(request, 'reports/exam_form.html', {'form': form, 'title': 'Add Exam'})

# View to edit an exam
def edit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if request.method == "POST":
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            return redirect('exam_list')
    else:
        form = ExamForm(instance=exam)
    
    return render(request, 'reports/exam_form.html', {'form': form, 'title': 'Edit Exam'})

# View to delete an exam
def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if request.method == "POST":
        exam.delete()
        return redirect('exam_list')
    
    return render(request, 'reports/confirm_delete.html', {'object': exam, 'title': 'Delete Exam'})
