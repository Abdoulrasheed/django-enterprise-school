from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from utils.decorators import admin_required

@login_required
@admin_required
def send_bulk_sms(request):
	sms = Sms.objects.all()
	if request.method == "POST":
		form = SmsForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data.get('title')
			sms_body = form.cleaned_data.get('body')
			recipients = form.cleaned_data.get('to_user')
			current_session = Session.objects.get(current_session=True)


			if recipients == "Admin":
				users = User.objects.filter(is_superuser=True)
			elif recipients == "Student":
				users = Student.objects.filter(session=current_session)
			elif recipients == "Parent":
				users = User.objects.filter(is_parent=True)
			elif recipients == "Teacher":
				users = User.objects.filter(is_teacher=True)

			for user in users:
				asyncio.run(send_sms(
					phone_number = user.user.phone, 
					request = request,
					msg_body = '{}, {}'.format(title, sms_body)
					)
				)
			sms = Sms.objects.create(
				title=title, 
				body=sms_body, 
				to_user=recipients,
				status=DELIVERED).save()
			messages.success(request, ' Messages delivered successfully')
			context = {
				"sms": sms,
				"title": title,
				"body": sms_body,
				"to_user": recipients
			}
			return render(request, 'sms.html', context)
		else:
			form = SmsForm(request.POST)
			context = {"form": form}
			return render(request, 'sms.html', context)
	else:
		context = {"sms":sms}
		return render(request, 'sms.html', context)

@login_required
@admin_required
def sms_list(request):
	sms = Sms.objects.all()
	return render(request, 'sms.html', {"sms":sms})


@login_required
@admin_required
def mail(request):
	if request.method == "POST":
		form = EmailMessageForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data.get('title')
			message = form.cleaned_data.get('message')
			image = form.cleaned_data.get('image')
			recipients = form.cleaned_data.get('recipients')

			# get author of the email
			admin = request.user

			mail = EmailMessage.objects.create(
				title=title,
				content=message,
				admin=admin
			)
			mail.save()

			# prepare html templates
			template = 'email_template.html'
			setting = Setting.objects.first()
			context= {
				'setting': setting,
				'mail': mail
				}

			mail_message = render_to_string(template, context)
			
			# add recipients one after another
			for i in recipients:
				mail.recipients.add(i)
				

			# send the actual email and redirect
			asyncio.run(mail.deliver_mail(content=mail_message, request=request))
			return redirect('mail')
		else:
			form = EmailMessageForm(request.POST)
			context = {"form": form}
			template = 'mail/mail_view.html'
			return render(request, template, context)

	draft_mails = EmailMessage.objects.filter(status=PENDING)
	delivered_mails = EmailMessage.objects.filter(status=DELIVERED)
	context = {
		'draft_mails': draft_mails,
		'delivered_mails': delivered_mails
	}
	template = 'mail/mail_view.html'
	return render(request, template, context)



@login_required
@admin_required
def save_draft_mail(request):
	if request.is_ajax():
		data = request.GET
		title = data.get('title')
		body = data.get('body')
		recipients = data.getlist('recipients[]')
		mails = EmailMessage.objects.create(
			admin=request.user,
			title=title,
			content=body,
		)

		mails.recipients.set(recipients)
		mails.save()
		return HttpResponse('success')