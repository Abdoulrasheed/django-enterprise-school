from .import views
from django.urls import path, include

urlpatterns = [
	path('', views.home, name="home_page"),
	path('promotion/', include('promotion.urls')),
	path('report/', include('reports.urls')),
	path('user/', include('users.urls')),
	path('sms/', include('sms_notification.urls')),
	path('attendance/', include('attendance.urls')),

	path('class/', views.ClassView.as_view(), name="class_list"),
	path('class/add/', views.AddClass.as_view(), name="add_class"),
	path('class/del<int:id>/', views.delete_class, name="delete_class"),

	path('batch/', views.BatchList.as_view(), name='batch_list'),
	path('batch/add/', views.AddBatch.as_view(), name="add_batch"),
	path('batch/del/<int:pk>/', views.DeleteBatch.as_view(), name="delete_batch"),
	path('batch/change/<int:pk>/', views.UpdateBatch.as_view(), name="edit_batch"),
	path('ajax/load-batches/', views.load_batches, name='ajax_load_batches'),

	path('subjects/', views.SubjectListView.as_view(), name="subjects_list"),
	path('subjects/add/', views.SubjectAddView.as_view(), name="add_subject"),
	path('subjects/del<int:id>/', views.delete_subject, name="delete_subject"),
	path('subjects/allocation/', views.SubjectAllocationList.as_view(), name="subject_allocation_list"),
	path('subjects/allocation/view/', views.assign_teacher_view, name="assign_teacher_view_list"),
	path('subjects/allocation/del<int:id>/', views.delete_all_allocated_subjects, name="delete_all_allocated_subjects"),
	path('subject/allocation/add/', views.AddSubjectAllocation.as_view(), name="add_subject_allocation"),
	
	path('sections/allocation/', views.section_allocation, name="section_allocation"),
	path('sections/allocation/add/', views.add_section_allocation, name="add_assign_section"),
	path('sections/allocation/del<int:id>/', views.delete_section_allocation, name="del_section_allocation"),
	path('section/', views.section_view, name="sections_list"),
	path('section/add/', views.add_section, name="add_section"),
	path('section/del<int:id>/', views.delete_section, name="delete_section"),


	path('score/', views.ScoreListView.as_view(), name="score_list"),
	path('score/view/', views.view_score, name="view_score_list"),
	path('score/entry/add/', views.ScoreEntry.as_view(), name="score_entry"),
	path('score/classes/', views.get_section_classes, name='get_section_classes'),
	path('score/batches/', views.get_section_classes, name='get_section_classes'),


	path('api/chart/', views.expenditure_graph, name="expense_graph_url"),

	path('subjects/getforsection/', views.load_subjects_by_section, name='load_subjects_by_section'),
	path('toggle-academicyear/<int:id>/', views.toggle_session, name="toggle_session"),
	
	path('expenditure/', views.expenditure, name="view_expenses"),
	path('expenditure/add/', views.add_expenditure, name="add_expense"),
	path('expenditure/del<int:id>/', views.delete_expenditure, name="delete_expense"),

	path('payment/', views.payment, name="view_payments"),
	path('payment/add/', views.add_payment, name="add_payment"),
	path('payment/set/', views.set_payment, name="set_payment"),
	path('payment/del<int:id>/', views.payment, name="delete_payment"),

	path('session/', views.session_view, name="session_list"),
	path('session/add/', views.add_session, name="add_session"),
	path('session/del<int:id>/', views.del_session, name="delete_session"),
	path('session/edit/<int:id>/', views.update_session, name='edit_session'),

	path('online_admission/', views.online_admission_list, name="online_admission_list"),
	path('settings/', views.general_setting, name="general_setting"),
	path('ajax/score/list/', views.load_score_table, name="ajax_load_load_score_table"),
	path('ajax/load/subjects/', views.load_subjects, name='ajax_load_subjects'),

	path('ajax/load/payment/', views.load_payment_table, name="ajax_load_payments"),
	path('ajax/load/students/', views.load_students_of_class, name="ajax_load_students"),
	path('ajax/load/students/users/', views.load_student_users, name="ajax_load_student_users"),

	path('grade_scale/', views.GradeScaleListView.as_view(), name="grade_scale"),
	path('grade_scale/add/', views.GradeScaleCreateView.as_view(), name="set_grade_scale"),
	path('grade_scale/edit/<int:pk>/', views.GradeScaleUpdateView.as_view(), name="edit_grade_scale"),
	path('grade_scale/add/<int:pk>/', views.GradeScaleDeleteView.as_view(), name="delete_grade_scale"),
	path('grade_scale/modal/', views.get_gradescale_form_modal, name="grade_scale_modal"),

	

	path('notice/', views.notice_board, name="notice_board"),
	path('notice/post', views.create_notice, name="create_notice"),
	path('notice/del<int:id>/', views.delete_notice, name="delete_notice"),

    path('class/edit/<int:id>/', views.update_class, name='edit_class'),
	path('subject/edit/<int:id>/', views.update_subject, name='edit_subject'),
	path('section/edit/<int:id>/', views.update_section, name='edit_section'),
	path('expense/edit/<int:id>/', views.update_expense, name='edit_expense'),
	path('section-allocation/edit/<int:id>/', views.update_section_allocation, name='edit_section_allocation'),
	
	path('set/parent/', views.set_parent, name="set_parent"),

	path('onlineadmission/applicant/<int:pk>/view/', views.view_detail_applicant, name='view_detail_applicant'),
	path('ajax/classes/', views.ajax_get_all_classes, name='get_classes'),

	path('ajax/seekrenewal/', views.ajax_seek_renewal, name='seek_renewal'),

	path('syllabus/', views.subject_syllabus, name='subject_syllabus'),

	path('import/score/', views.import_scores, name='import_scores'),

	path('roles/', views.RoleView.as_view(), name='sms_roles_view'),
	path('roles/add/', views.RoleAddView.as_view(), name='sms_roles_add'),

	path('mark_percentage/', views.MarkPercentageView.as_view(), name='mark_percentage'),
	path('mark_percentage/add/', views.AddMarkPercentageView.as_view(), name='add_mark_percentage'),
	path('mark_percentage/change/<int:pk>/', views.UpdateMarkPercentageView.as_view(), name='update_mark_percentage'),
	path('mark_percentage/delete/<int:pk>/', views.DeleteMarkPercentageView.as_view(), name='delele_mark_percentage'),
	path('mark/permission/', views.MarkPermissionCreateView.as_view(), name='mark_permission'),
	path('mark/permission/create/', views.MarkPermissionCreateView.as_view(), name='create_mark_permission'),
	path('persmissions/', views.PermissionView.as_view(), name='sms_permissions_view'),
	path('ajax/loadpersmissions/', views.loadpersmissions, name='ajax_loadpersmissions'),
	path('ajax/optional_subjects/', views.get_batch_optional_subjects, name='batch_optional_subjects'),
	]