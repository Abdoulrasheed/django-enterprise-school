from django.shortcuts import render

# Create your views here.
def home(request):
	return render(request, 'clc_main/home.html', {}) 

def courses(request):
	return render(request, 'clc_main/course_list.html', {})


def aboutus(request):
	return render(request, 'clc_main/contact.html', {})