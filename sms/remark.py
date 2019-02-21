from .constants import *
from .models import GradeScale

def getRemark(total):
	gradeScale = GradeScale.objects.all()
	for i in gradeScale:
		if total in range(i.mark_from, i.mark_upto+1):
			print(i.remark)
			return i.remark

def getGrade(total):
	gradeScale = GradeScale.objects.all()
	for i in gradeScale:
		if total in range(i.mark_from, i.mark_upto+1):
			print(i.grade)
			return i.grade