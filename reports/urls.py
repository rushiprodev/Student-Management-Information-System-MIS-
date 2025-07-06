from django.urls import path
from . import views
from .views import attendance_pdf, topper_pdf, defaulter_pdf, register, user_login, user_logout, edit_student, delete_student, edit_attendance, delete_attendance, exam_list, add_exam, edit_exam, delete_exam

urlpatterns = [
    path('', views.home, name='home'),
    path('students/', views.student_list, name='student_list'),
    path('attendance/', views.attendance_report, name='attendance_report'),
    path('exam/', views.exam_report, name='exam_report'),
    path('toppers/', views.topper_report, name='topper_report'),
    path('defaulters/', views.defaulter_report, name='defaulter_report'),

    path('attendance_pdf/', attendance_pdf, name='attendance_pdf'),
    path('topper_pdf/', topper_pdf, name='topper_pdf'),
    path('defaulter_pdf/', defaulter_pdf, name='defaulter_pdf'),

    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('graphical-report/', views.graphical_report, name='graphical_report'),

    path('student/edit/<str:reg_no>/', edit_student, name='edit_student'),
    path('student/delete/<str:reg_no>/', delete_student, name='delete_student'),

    path('attendance/edit/<int:attendance_id>/', edit_attendance, name='edit_attendance'),
    path('attendance/delete/<int:attendance_id>/', delete_attendance, name='delete_attendance'),

    path('exams/', exam_list, name='exam_list'),
    path('exams/add/', add_exam, name='add_exam'),
    path('exams/edit/<int:exam_id>/', edit_exam, name='edit_exam'),
    path('exams/delete/<int:exam_id>/', delete_exam, name='delete_exam'),

]
