from .import views
from django.urls import path

urlpatterns = [
	path('', views.home, name="home_page"),
	path('students/', views.students_view, name="students_list"),
	path('students/<int:id>/', views.students_list_view, name="students_list_view"),
	path('students/add/', views.add_student, name="add_student"),
	path('users/del<int:id>/', views.delete_user, name="delete_user"),
	path('parents/', views.parents_view, name="parents_list"),
	path('parents/add/', views.add_parent, name="add_parent"),
	path('teachers/', views.teachers_view, name="teachers_list"),
	path('teachers/add/', views.add_teacher, name="add_teacher"),
	path('class/', views.class_view, name="class_list"),
	path('class/add/', views.add_class, name="add_class"),
	path('class/del<int:id>/', views.delete_class, name="delete_class"),
	path('subjects/', views.subjects_view, name="subjects_list"),
	path('subjects/add/', views.add_subject, name="add_subject"),
	path('subjects/del<int:id>/', views.delete_subject, name="delete_subject"),
	path('subjects/allocation/', views.assign_teacher_list, name="assign_teacher_list"),
	path('subjects/allocation/view/', views.assign_teacher_view, name="assign_teacher_view_list"),
	path('subjects/allocation/del<int:id>/', views.delete_all_allocated_subjects, name="delete_all_allocated_subjects"),
	path('subject/allocation/add/', views.add_assign_teacher, name="add_assign_teacher"),
	path('sections/allocation/', views.section_allocation, name="section_allocation"),
	path('sections/allocation/add/', views.add_section_allocation, name="add_assign_section"),
	path('sections/allocation/del<int:id>/', views.delete_section_allocation, name="del_section_allocation"),
	path('section/', views.section_view, name="sections_list"),
	path('section/add/', views.add_section, name="add_section"),
	path('section/del<int:id>/', views.delete_section, name="delete_section"),
	path('attendance/', views.attendance_list, name="attendance_list"),
	path('attendance/add/', views.add_attendance, name="add_attendance"),
	path('attendance/save/', views.save_attendance, name="save_attendance"),
	path('attendance/del<int:id>/', views.delete_attendance, name="delete_attendance"),
	path('score/entry/', views.score_list, name="score_list"),
	path('score/entry/add/', views.score_entry, name="score_entry"),
	path('api/chart/', views.expenditure_graph, name="expense_graph_url"),
	path('system/administrators/', views.system_admin, name="system_admin"),
	path('system/administrators/add/', views.add_system_admin, name="add_system_admin"),
	path('profile/<int:user_id>/', views.profile, name="profile"),
	path('toggle-academicyear/<int:id>/', views.toggle_session, name="toggle_session"),
	path('score/view/', views.view_score, name="view_score_list"),
	path('expenditure/', views.expenditure, name="view_expenses"),
	path('expenditure/add/', views.add_expenditure, name="add_expense"),
	path('expenditure/del<int:id>/', views.delete_expenditure, name="delete_expense"),
	path('payment/', views.payment, name="view_payments"),
	path('payment/add/', views.add_payment, name="add_payment"),
	path('payment/set/', views.set_payment, name="set_payment"),
	path('payment/del<int:id>/', views.payment, name="delete_payment"),
	path('session/', views.session_view, name="session_list"),
	path('session/add/', views.add_session, name="add_session"),
	path('sms/', views.sms_list, name="sms_list"),
	path('mail/', views.mail, name="mail"),
	path('users-password/', views.reset_users_password, name="reset_users_password"),
	path('reset/', views.reset_users_password_view, name="reset_users_password_view"),
	path('sms/send/', views.send_bulk_sms, name="send_sms"),
	path('online_admission/', views.online_admission_list, name="online_admission_list"),
	path('settings/', views.general_setting, name="general_setting"),
	path('session/del<int:id>/', views.del_session, name="delete_session"),
	path('ajax/score/list/', views.load_score_table, name="ajax_load_load_score_table"),
	path('ajax/load/subjects/', views.load_subjects, name='ajax_load_subjects'),
	path('ajax/load/payment/', views.load_payment_table, name="ajax_load_payments"),
	path('ajax/load/students/', views.load_students_of_class, name="ajax_load_students"),
	path('ajax/load/students/users/', views.load_student_users, name="ajax_load_student_users"),
	path('report/student/', views.create_report_student, name="create_report_student"),
	path('report/pdf/', views.report_student, name="report_student"),
	path('grade-scale/', views.grade_scale, name="grade_scale"),
	path('set-grade-scale/', views.set_grade_scale, name="set_grade_scale"),
	path('promotion/', views.promotion, name="promotion_list"),
	path('ajax-load-to-class-list/', views.to_class_list, name="to_class_list"),
	path('ajax-load-promotion-list', views.load_promotion_list, name="load_promotion_list"),
	path('promote/<int:stud_id>/<int:to_class_id>/<int:to_session_id>/', views.promote, name="promote"),
	path('notice/', views.notice_board, name="notice_board"),
	path('notice/post', views.create_notice, name="create_notice"),
	path('notice/del<int:id>/', views.delete_notice, name="delete_notice"),
	path('student/edit/<int:id>/', views.update_student, name="edit_student"),
	path('user/edit/<int:id>/', views.update_user, name="edit_user"),
    path('class/edit/<int:id>/', views.update_class, name='edit_class'),
	path('subject/edit/<int:id>/', views.update_subject, name='edit_subject'),
	path('section/edit/<int:id>/', views.update_section, name='edit_section'),
	path('expense/edit/<int:id>/', views.update_expense, name='edit_expense'),
	path('section-allocation/edit/<int:id>/', views.update_section_allocation, name='edit_section_allocation'),
	path('session/edit/<int:id>/', views.update_session, name='edit_session'),
	path('user/toggle/<int:id>/', views.toggle_user_status, name='toggle_user_status'),
	path('set/parent/', views.set_parent, name="set_parent"),
	path('user/upload-profile-picture', views.upload_picture, name="upload_profile_picture"),
	path('class_members/', views.class_member_report_view, name="class_members_report_view"),
	path('class_members/report', views.class_member_report, name="class_members_report"),
	path('subject_allocation/', views.subject_allocation_report_view, name="subject_allocation_report_view"),
	path('subject_allocation/report/', views.subject_allocation_report, name="subject_allocation_report"),
	path('subject/report/view', views.subject_report_view, name="subject_report_view"),
	path('subject/report/', views.subject_report, name="subject_report"),
	path('broadsheet/report/view', views.broadsheet_report_view, name="broadsheet_report_view"),
	path('broadsheet/report/', views.broadsheet_report, name="broadsheet_report"),
	path('onlineadmission/applicant/<int:pk>/view/', views.view_detail_applicant, name='view_detail_applicant'),
	path('ajax/classes/', views.ajax_get_all_classes, name='get_classes'),
	path('ajax/users/', views.ajax_get_users_list, name='get_users_list'),
	]