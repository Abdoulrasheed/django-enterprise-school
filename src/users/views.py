import random
from django.views import View
from django.urls import reverse
from django.contrib import messages
from authentication.models import User
from utils.helper import BulkCreateManager
from django.contrib.auth.models import Group
from django.utils.decorators import method_decorator
from sms.models import Class, Session, Student, Teacher
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from utils.decorators import teacher_required, admin_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from django.views.generic import DetailView, TemplateView, CreateView, ListView
from .forms import AddStudentForm, AddUserForm, AddTeacherForm
from utils.decorators import admin_required

@method_decorator(admin_required, name='dispatch')
class StudentView(TemplateView):
	template_name = 'student/student_list.html'
	model = Student

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		classes = Class.objects.all()
		context["classes"] = classes
		return context


@login_required
@teacher_required
def students_list_view(request, id):
    current_session = Session.objects.get(current_session=True)
    students = Student.objects.filter(in_class__pk=id, session=current_session)
    selected_class = Class.objects.get(pk=id)
    classes = Class.objects.all()

    # if teacher, then show only classes
	# that he/she is been assigned a subject in.
	# for current academic year, and current term

    if request.user.is_teacher:
    	current_session = Session.objects.get_current_session()
    	classes = SubjectAssign.objects.filter(
    		teacher__id=request.user.id, 
			session=current_session, 
			term=get_terms())
    context = {
        "selected_class": selected_class,
        "students": students,
        "classes": classes,
        }
    return render(request, 'student/student_list.html', context)


@method_decorator(login_required, name='dispatch')
class AddStudent(View):
	form_classes = [AddStudentForm, AddUserForm]
	template_name = 'student/student_form.html'

	def get(self, request):
		form = self.form_classes
		return render(request, self.template_name, {"form": form})
		

	def post(self, request):
		student_form = self.form_classes[0](request.POST)
		user_form = self.form_classes[1](request.POST, request.FILES)

		def get_student_data(selected_class):
			counter = Student.objects.filter(in_class=selected_class).count()
			student_id = "STU{0:03}".format(counter+1)
			roll_number = "{0:03}".format(counter+1)
			return [student_id, roll_number]

		def generate_password():
			password = f'{random.randrange(1, 10**3):04}'
			return make_password(password)
		
		if all([user_form.is_valid(), student_form.is_valid()]):
			user = user_form.save(commit=False)
			selected_class = student_form.cleaned_data.get('in_class')
			student_data = get_student_data(selected_class)
			user.username = student_data[0]
			user.password = generate_password()
			user.save()

			group = Group.objects.get(name='student') 
			group.user_set.add(user.pk)

			student = student_form.save(commit=False)
			student.user = user
			student.session = Session.objects.get_current_session()
			student.roll_number = student_data[1]
			student.save()

			messages.success(request, "Successfully added")
			return redirect('students_list')
		else:
			ct = {"form": [user_form, student_form]}
			return render(request, self.template_name, ct)


@login_required
@admin_required
def update_student(request, id):
	student = get_object_or_404(Student, id=id)
	user = get_object_or_404(User, id=student.user.id)
	template_name = 'student/student_form.html'
	if request.method == "POST":
		userForm = AddUserForm(request.POST, instance=user)
		studentForm = AddStudentForm(request.POST, instance=student)
		if all([userForm.is_valid(), studentForm.is_valid()]):
			user = userForm.save()
			student = studentForm.save()
			messages.success(request, f"Successfully updated {user.username}'s information")
			return redirect('students_list')
		else:
			userForm = AddUserForm(request.POST, request.FILES)
			studentForm = AddStudentForm(request.POST)
			form = [studentForm, userForm]
			context = {
				'form':form,
			}
			return render(request, template_name, context)
	else:
		userForm = AddUserForm(instance=user)
		studentForm = AddStudentForm(instance=student)
		form = [studentForm, userForm]
		context = { 'form': form }
	return render(request, template_name, context)



@method_decorator(teacher_required, name='dispatch')
class TeacherView(ListView):
	template_name = 'teacher/teacher_list.html'
	model = Teacher

@method_decorator(admin_required, name='dispatch')
class AddTeacherView(View):
	form_classes = [AddTeacherForm, AddUserForm]
	template_name = 'teacher/teacher_form.html'

	def get(self, request):
		form = self.form_classes
		return render(request, self.template_name, {"form": form})
		

	def post(self, request):
		teacher_form = self.form_classes[0](request.POST)
		user_form = self.form_classes[1](request.POST, request.FILES)

		def generate_username():
			counter = Teacher.objects.count()
			teacher_id = "TEA{0:03}".format(counter+1)
			return teacher_id

		def generate_password():
			password = f'{random.randrange(1, 10**3):04}'
			print(password)
			return make_password(password)
		
		if all([user_form.is_valid(), teacher_form.is_valid()]):
			user = user_form.save(commit=False)
			user.username = generate_username()
			user.password = generate_password()
			user.save()

			group = Group.objects.get(name='teacher') 
			group.user_set.add(user.pk)

			teacher = teacher_form.save(commit=False)
			teacher.user = user
			teacher.save()
			messages.success(request, "Successfully added")
			return redirect('teachers_list')
		else:
			ct = {"form": [user_form, teacher_form]}
			return render(request, self.template_name, ct)


@login_required
@admin_required
def update_teacher(request, id):
	teacher = get_object_or_404(Teacher, id=id)
	user = get_object_or_404(User, id=teacher.user.id)
	template_name = 'teacher/teacher_form.html'
	if request.method == "POST":
		user_form = AddUserForm(request.POST, request.FILES, instance=user)
		teacher_form = AddTeacherForm(request.POST, instance=teacher)
		if all([user_form.is_valid(), teacher_form.is_valid()]):
			user = user_form.save()
			teacher = teacher_form.save()
			messages.success(request, f"Successfully updated {user.username}'s information")
			return redirect('teachers_list')
		else:
			user_form = AddUserForm(request.POST, request.FILES)
			teacher_form = AddTeacherForm(request.POST)
			form = [teacher_form, user_form]
			context = {
				'form':form,
			}
			return render(request, template_name, context)
	else:
		user_form = AddUserForm(instance=user)
		teacher_form = AddTeacherForm(instance=teacher)
		form = [teacher_form, user_form]
		context = { 'form': form }
	return render(request, template_name, context)


@login_required
@admin_required
def delete_user(request, id):
	user = User.objects.get(pk=id)
	if user:
		user_name = user.get_full_name()
		if user.is_student:
		    current_session = Session.objects.get(current_session=True)
		    student = Student.objects.get(user__pk=user.pk, session=current_session)
		    class_id = student.in_class.pk
		    student.delete()
		    new_students_list = Student.objects.filter(in_class__pk=class_id, session=current_session)
		    context = {'students': new_students_list,}
		    return render(request, 'student/new_students_list.html', context)
		elif user.is_teacher:
			user.delete()
			new_teachers_list = User.objects.filter(is_teacher=True)
			context = {'teachers': new_teachers_list,}
			return render(request, 'teacher/new_teachers_list.html', context)
		elif user.is_parent:
			user.delete()
			new_parents_list = User.objects.filter(is_parent=True)
			context = {
				'parents': new_parents_list,
			}
			return render(request, 'parent/new_parents_list.html', context)
		else:
			user.delete()
			messages.success(request, user_name + ' Successfully deleted !')
			return redirect('home')
	else:
		return HttpResponse('user not found')


@login_required
@admin_required
def parents_view(request):
	parents = User.objects.filter(is_parent=True)
	context = {
		'parents': parents,
	}
	return render(request, 'parent/parent_list.html', context)


@login_required
@admin_required
def add_parent(request):
	context = {}
	if request.method == "POST":
		form = AddParentForm(request.POST, request.FILES)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			firstname = form.cleaned_data.get('firstname')
			surname = form.cleaned_data.get('surname')
			othername = form.cleaned_data.get('othername')
			state = form.cleaned_data.get('state')
			phone = form.cleaned_data.get('phone')
			email = form.cleaned_data.get('email')
			address = form.cleaned_data.get('address')
			picture = form.cleaned_data['picture']
			full_name = firstname+" "+surname
			if User.objects.filter(username=username).exists():
				messages.success(request, "A user with username "+ username + " had already exists !")
				return HttpResponseRedirect(reverse_lazy('add_parent'))
			User.objects.create(
				username=username,
				password=make_password(password),
				first_name=firstname,
				last_name=surname,
				other_name=othername,
				address=address,
				state=state,
				phone=phone,
				email=email,
				picture=picture,
				is_parent=True,
				)
			if picture:
				fs = FileSystemStorage()
				fs.save(picture.name, picture)
			messages.success(request, firstname + " " + surname +' Was Successfully Recorded! ')
			
			sms_body="Hello {0}, \
					You can now access any of your child's school \
					record right from your mobile or pc device!\nLogin \
					using the link and the credentials below and we recommend \
					you change your password immediately.\
					username: {1}\
					password: {2}\
					link: {3}".format(
						full_name, 
						username, 
						password, 
						request.META['HTTP_HOST']
						)

			send_sms(phone_number=phone, request=request, msg_body=sms_body)

			return HttpResponseRedirect(reverse_lazy('add_parent'))
		else:
			form = AddParentForm(request.POST, request.FILES)
			context =  {
				"form": form,
				}
	return render(request, 'parent/parent_form.html', context)


@login_required
@admin_required
def system_admin(request):
	users = User.objects.filter(is_superuser=True)
	return render(request, 'user/user_list.html', { "users": users })

@login_required
@admin_required
def add_system_admin(request):
	context = {}
	if request.method == "POST":
		form = AddParentForm(request.POST, request.FILES)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			firstname = form.cleaned_data.get('firstname')
			surname = form.cleaned_data.get('surname')
			othername = form.cleaned_data.get('othername')
			state = form.cleaned_data.get('state')
			phone = form.cleaned_data.get('phone')
			email = form.cleaned_data.get('email')
			address = form.cleaned_data.get('address')
			picture = form.cleaned_data['picture']

			if User.objects.filter(username=username).exists():
				messages.success(request, "A user with username "+ username + " had already exists !")
				return HttpResponseRedirect(reverse_lazy('add_system_admin'))
			User.objects.create(
				username=username,
				password=make_password(password),
				first_name=firstname,
				last_name=surname,
				other_name=othername,
				address=address,
				state=state,
				phone=phone,
				email=email,
				picture=picture,
				is_superuser=True,
				)
			messages.success(request, firstname + " " + surname +' Was Successfully Recorded! ')
			return HttpResponseRedirect(reverse_lazy('add_system_admin'))
		else:
			form = AddParentForm(request.POST, request.FILES)
			context =  {
				"form": form,
				}
	return render(request, 'user/user_form.html', context)


@login_required
@admin_required
def reset_users_password_view(request):
	if request.is_ajax():
		if request.method == 'POST':
			user = request.POST.get('selected_user')
			new_pass = request.POST.get('new_password')
			user = User.objects.get(username=user)
			user.password = make_password(new_pass)
			user.save()
	return render(request, 'user/users_password_form.html', {})


@login_required
@admin_required
def reset_users_password(request):
	user_type = request.GET.get('user_type')
	if user_type == 'admin':
		users = User.objects.filter(is_superuser=True)
	elif user_type == 'student':
		users = User.objects.filter(is_student=True)
	elif user_type == 'parent':
		users = User.objects.filter(is_parent=True)
	elif user_type == 'teacher':
		users = User.objects.filter(is_teacher=True)
	context = {'users': users}
	return render(request, 'sms/load_users.html', context)


@login_required
@admin_required
def update_user(request, id):
	user = get_object_or_404(User, id=id)
	if user.is_student:
		user_type = "Student"
	elif user.is_teacher:
		user_type = "Teacher"
	elif user.is_parent:
		user_type = "Parent"
	else:
		user_type = "Administrator"
	if request.method == "POST":
		form = EditUserForm(request.POST, instance=user)
		if form.is_valid():
			user = form.save(commit=False)
			user.first_name = form.cleaned_data.get('first_name')
			user.last_name = form.cleaned_data.get('last_name')
			user.other_name = form.cleaned_data.get('other_name')
			user.religion = form.cleaned_data.get('religion')
			user.address = form.cleaned_data.get('address')
			user.gender = form.cleaned_data.get('gender')
			user.phone = form.cleaned_data.get('phone')
			User.email = form.cleaned_data.get('email')
			user.dob = form.cleaned_data.get('dob')
			user.state = form.cleaned_data.get('state')
			user.save()
			messages.success(request, 'Successfully updated {0}\'s information '.format(user.username))
			return redirect('edit_user', id=user.id)
		else:
			form = EditUserForm(request.POST)
			context = {'form': form, 'user_type': user_type}
			return render(request, 'user/user_form.html', context)
	else:
		form = EditUserForm(instance=user)
		context = {'form': form, 'user_type': user_type}
		return render(request, 'user/user_form.html', context)


@login_required
@admin_required
def toggle_user_status(request, id):
	user = get_object_or_404(User, id=id)
	if request.user.id == user.id:
		return HttpResponse('You cannot deactivate yourself')
	elif user.is_active:
		user.is_active = False
		user.save()
		return HttpResponse('deactivated')
	else:
		user.is_active = True
		user.save()
		return HttpResponse('activated')


@login_required
def upload_picture(request):
	if request.is_ajax:
		form = ProfilePictureForm(request.POST, request.FILES)
		if form.is_valid():
			picture = form.cleaned_data.get('picture')
			user = get_object_or_404(User, id=request.user.id)
			user.picture = picture
			user.save()
			fs = FileSystemStorage()
			fs.save(picture.name, picture)
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		else:
			form = ProfilePictureForm(request.POST, request.FILES)
			messages.success(request, form.errors)
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



@login_required
def change_password(request):
    from django.contrib.auth import update_session_auth_hash
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_pass = form.cleaned_data.get('old_password')
            new_pass = form.cleaned_data.get('new_password')
            confirm_password = form.cleaned_data.get('confirm_password')
            user = request.user
            old_p = user.password
            new_p = make_password(new_pass)
            if user.check_password(old_pass):
                if new_pass == confirm_password:
                    user.password = new_p
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Your password was successfully updated!')
                    return redirect('change_password')
                else:
                    messages.success(request, 'New password and confirmed password do not match !')
                    return redirect('change_password')
            else:
                messages.success(request, 'Old password is incorrect, you may contact the principal if this parsist !')
                return redirect('change_password')
        else:
            form = ChangePasswordForm(request.POST)
            return render(request, 'sms/users/change_password.html', {'form': form})
    else:
        return render(request, 'sms/users/change_password.html', {})

@login_required
@admin_required
def ajax_get_users_list(request):
	if request.is_ajax():
		template = 'sms/ajax/get_filtered_user_list.html'
		user_type = request.GET.get('user_type')
		print(user_type)
		if user_type == 'parents':
			users = User.objects.filter(is_parent=True)
		elif user_type == 'admins':
			users = User.objects.filter(is_superuser=True)
		elif user_type == 'teachers':
			users = User.objects.filter(is_teacher=True)
		context = {'users': users}
		return render(request, template, context)
	return HttpResponse('error')


@login_required
def import_users(request):
	import codecs
	template = 'import/import_view.html'
	form = ImportForm(request.FILES)
	if request.method == "POST":
		#if form.is_valid():
		#file = form.cleaned_data.get('csv_file')

		file = request.FILES['csv_file']
		bulk_mgr = BulkCreateManager(chunk_size=20)
		reader = csv.reader(codecs.iterdecode(file, 'utf-8'))
		next(reader, None)  # skip the headers
		for row in reader:
			print(row[0])
			roll = generate_role_number()
			class_ = Class.objects.filter(name=row[3]).first()
			if class_:
				student = User.objects.create(
					username=roll,
					password=generate_password(),
					first_name=row[0],
					last_name=row[1],
					other_name=row[2],
					is_student=True)
				student.save()
				session = Session.objects.get(current_session=True)
				bulk_mgr.add(
					Student(user=student, in_class=class_,session=session, roll_number=roll))
				bulk_mgr.done()
			else:
				print('theres an error')
		messages.success(request, 'Successfully added')
		return redirect('import_users')
	else:
		return render(request, template, {})


@method_decorator(login_required, name='dispatch')
class UserProfileView(DetailView):
	model = User
	template_name = 'user/user_profile.html'


@login_required
def download_template(request):
	import os
	file = 'data/student_template.csv'
	filename = os.path.join(BASE_DIR, file)

	data = open(filename, 'r').read()
	response = HttpResponse(data, content_type='application/x-download')
	response['Content-Disposition'] = 'attachment;filename={}.csv'.format('student_template')
	return response