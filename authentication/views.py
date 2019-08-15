from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext

def login_request(request):
	if request.is_ajax():
		username = request.GET.get('username')
		password = request.GET.get('password')
		user = authenticate(username=username, password=password)
		if user is not None:
			#if user.is_active and user.is_superuser and user.is_site_su:
			if user.is_active:
				login(request, user)
				return HttpResponse(1)
			else:
				return HttpResponse('Invalid login')
		else:
			return HttpResponse('Invalid login')
	else:
		template = 'authentication/login.html'
		return render(request, template, {})


def logout_request(request):
	context = RequestContext(request)
	logout(request)
	# Redirect back to index page.
	return HttpResponseRedirect('/login/')