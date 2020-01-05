from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from utils.decorators import admin_required, teacher_required
from django.http import HttpResponseRedirect


@login_required
@teacher_required
def attendance_list(request):
	session = Session.objects.get(current_session=True)
	all_class = Class.objects.all()
	if request.method == "POST":
		date = request.POST['date']
		if date == '':
			messages.info(request, "Please select class, term and date in order to view attendance")
			return HttpResponseRedirect(reverse_lazy('attendance_list'))
		date = datetime.strptime(date, '%d %B, %Y')
		form = AttendanceListForm(request.POST)
		if form.is_valid():
			term = form.cleaned_data.get('selected_term')
			selected_class = form.cleaned_data.get('selected_class')
			students = Student.objects.filter(in_class=selected_class, session=session)
			ids = ()
			for i in students:
				ids += (i.user.pk,)
			q = Attendance.objects.filter(date=date, student__user__pk__in=ids, term=term, session=session)
			context = {
				"students": students,
				"classes": all_class,
				"attendance": q,
				"selected_class": selected_class,
				"selected_term": term,
				"selected_date": date,
			}
		else:
			context =  {
				"form": form,
				"classes": all_class,
			}
	else:
		context = {"classes": all_class}
	return render(request, 'student/attendance_list.html', context)


@login_required
@teacher_required
def attendance_view(request):
	current_session = Session.objects.all(current_session=True)
	select_class = Class.objects.filter(id=id)
	context = {"in_class": select_class}
	return render(request, 'student/attendance.html', context)

@login_required
@teacher_required
def add_attendance(request):
	current_session = Session.objects.get(current_session=True)
	if request.method == "POST":
		in_class = Class.objects.all()
		data = request.POST.copy()
		data.pop('csrfmiddlewaretoken')
		data.pop('submit')
		try:
			date = data['date']
			term = data['term']
			class_id = data['class']
			selected_class = Class.objects.get(pk=class_id)
			date = datetime.strptime(date, '%d %B, %Y')
			students = Student.objects.filter(in_class__pk=class_id, session=current_session)
			context = {
				"students": students,
				"classes": in_class,
				"selected_class": selected_class,
				"term": term,
				"date": date,
			}
		except:
			messages.info(request, "Please select class, term and date in order to add attendance")
			return HttpResponseRedirect(reverse_lazy('add_attendance'))
	else:
		in_class = Class.objects.all()
		context = {
			"classes": in_class,
		}
	return render(request, 'student/add_attendance.html', context)


@login_required
@teacher_required
def save_attendance(request):
	if request.method == 'POST':
		session = Session.objects.get(current_session=True)
		term = request.POST.get('selected_term')
		date = request.POST.get('selected_date')

		stud_id = list(request.POST.getlist('student_id'))
		status = list(request.POST.getlist('status'))
		is_late = list(request.POST.getlist('is_late'))
		duration = list(request.POST.getlist('duration'))

		if len(is_late) < len(stud_id):
			for i in range(0, len(stud_id)):
				is_late.append(False)

		if len(status) < len(stud_id):
			for i in range(0, len(stud_id)):
				status.append(False)

		for i in range(0, len(stud_id)):
			student = Student.objects.get(pk=stud_id[i])
			d = duration[i]
			if status[i] == 'on':
				s = True
			else:
				s = False

			if is_late[i] == 'on':
				is_l = True
			else:
				is_l = False

			try:
				a = Attendance.objects.get(student=student, term=term, session=session, date=date)
				a.is_late = is_l
				a.is_present = s
				a.is_late_for = d
				a.save()
			except Attendance.DoesNotExist:
				Attendance(
					student=student,
					term=term,
					session=session,
					is_present=s,
					is_late=is_l,
					date=date,
					is_late_for=d
					).save()
		messages.success(request, "Successfully saved")
		return redirect('add_attendance')
	else:
		messages.error(request, "There's an error while creating an attendance record")
		return redirect('add_attendance')


@login_required
@admin_required
def delete_attendance(request, id):
	attendance = Attendance.objects.get(pk=id)
	student = attendance.student
	date = attendance.date
	attendance.delete()
	messages.success(request, "You've successfully deleted "+ str(student) +" from attendance of " + str(date))
	return HttpResponseRedirect(reverse_lazy('attendance_list'))