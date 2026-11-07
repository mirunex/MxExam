from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Giriş ve Çıxış
    path('login/', views.user_login_view, name='login'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('superadmin-login/', views.superadmin_login_view, name='superadmin_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Paneller
    path('', views.dashboard_view, name='dashboard'),
    path('home/', views.dashboard_view, name='home'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('superadmin/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('superadmin/institutions/new/', views.institution_create_view, name='institution_create'),
    path('superadmin/institutions/<int:institution_id>/add-admin/', views.institution_admin_create_view, name='institution_admin_create'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/teachers/new/', views.teacher_create_view, name='teacher_create'),
    path('admin-panel/groups/', views.admin_groups_view, name='admin_groups'),
    path('admin-panel/students/new/', views.student_create_view, name='student_create'),
    path('admin-panel/students/import/', views.student_import_view, name='student_import'),
    path('admin-panel/students/import/confirm/', views.student_import_confirm_view, name='student_import_confirm'),
    path('admin-panel/groups/<int:group_id>/', views.admin_group_detail_view, name='admin_group_detail'),
    path('admin-panel/users/', views.admin_users_view, name='admin_users'),
    # İmtahan əməliyyatları  
    path('teacher/exam/delete/<int:exam_id>/', views.delete_exam_view, name='delete_exam'),
    path('teacher/exam/<int:exam_id>/add-question/', views.add_question_view, name='add_question'),
    path('teacher/groups/', views.teacher_groups, name='teacher_groups'),
    path('teacher/exam/<int:exam_id>/upload-pdf/', views.upload_exam_pdf, name='upload_exam_pdf'),
    path('student/exam/<int:exam_id>/', views.start_exam_view, name='start_exam'),
    path('teacher/exams/new/', views.create_exam_view, name='create_exam'),
    path('teacher/exams/<int:exam_id>/results/', views.exam_results_view, name='exam_results'),
    path('teacher/exams/<int:exam_id>/grade/<int:student_id>/', views.grade_written_view, name='grade_written'),
    path('student/exam/<int:exam_id>/run/', views.run_code_view, name='run_code'),
    path('student/exam/<int:exam_id>/submit-task/', views.submit_task_view, name='submit_task'),
    path('teacher/exams/<int:exam_id>/reset/<int:student_id>/', views.reset_result_view, name='reset_result'),
    path('student/exam/<int:exam_id>/violation/', views.exam_violation_view, name='exam_violation'),
    path('teacher/live/', views.teacher_live_view, name='teacher_live'),
    path('teacher/live/feed/', views.teacher_live_feed_view, name='teacher_live_feed'),
]