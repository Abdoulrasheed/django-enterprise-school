from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from utils.decorators import admin_required


@login_required
@admin_required
def promotion(request):
	classes = Class.objects.all()
	sessions = Session.objects.all()
	return render(request, 'sms/promotion/promote.html', {'sessions': sessions, 'classes': classes})


@login_required
@admin_required
def load_promotion_list(request):
	if request.is_ajax():
		from_class_id = request.GET.get('from_class_id')
		to_class_id = request.GET.get('to_class_id')
		current_session = Session.objects.get(current_session=True)
		to_session = request.GET.get('to_session')
		ranking = Student.objects.filter(in_class__pk=from_class_id, session=current_session)
		context = {
			'term': get_terms(),
			'current_session': current_session,
			'ranking': ranking,
 			'to_session': to_session,
          	'from_class_id': from_class_id,
          	'to_class_id': to_class_id,
		}
		return render(request, 'sms/promotion/load_promotion_list.html', context)


@login_required
@admin_required
def promote(request, stud_id,  to_class_id, to_session_id):
	from_session = Session.objects.get(current_session=True)
	to_session = Session.objects.get(id=to_session_id)
	to_class = Class.objects.get(id=to_class_id)

	student = Student.objects.get(
		id=stud_id, 
		session=from_session)

	# get the parent of the student if exist
	parent = student.guardians.first() or student.guardians.none()

	# create copy of the student object 
	# changing only the session and the class of the student
	student.pk = None
	student.session = to_session
	student.in_class = to_class
	student.save()

	# connect the copied student with a parent
	parent.student.add(student)

	return HttpResponse('Promoted')

@login_required
@admin_required
def to_class_list(request):
	if request.is_ajax:
		from_class = request.GET.get('from_class')
		classes = Class.objects.exclude(id=from_class)
		return render(request, 'sms/promotion/to_class_list.html', {'classes': classes})