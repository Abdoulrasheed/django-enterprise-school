from django.urls import path
from . import views

urlpatterns = [
	path('reportcard_sheet/', views.report_card_sheet_view, name="create_report_student"),
	path('reportcard_sheet/pdf', views.report_student, name="report_student"),

	path('class_members/', views.class_member_report_view, name="class_members_report_view"),
	path('class_members/pdf', views.class_member_report, name="class_members_report"),

	path('subject_allocation/', views.subject_allocation_report_view, name="subject_allocation_report_view"),
	path('subject_allocation/report/', views.subject_allocation_report, name="subject_allocation_report"),

	path('subject/', views.subject_report_view, name="subject_report_view"),
	path('subject/pdf/', views.subject_report, name="subject_report"),
	
	path('broadsheet/', views.broadsheet_report_view, name="broadsheet_report_view"),
	path('broadsheet/pdf/', views.broadsheet_report, name="broadsheet_report"),
]