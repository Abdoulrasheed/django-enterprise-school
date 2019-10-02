from constants import *
from .models import GradeScale

def getRemark(total):
	gradeScale = GradeScale.objects.all()
	for i in gradeScale:
		if total in range(i.mark_from, i.mark_upto+1):
			return i.remark

def getGrade(total):
	gradeScale = GradeScale.objects.all()
	for i in gradeScale:
		if total in range(i.mark_from, i.mark_upto+1):
			return i.grade

def getGradeWithTotalApproximate(total):
	total = round(total, 0)
	gradeScale = GradeScale.objects.all()
	for i in gradeScale:
		if total in range(i.mark_from, i.mark_upto+1):
			return i.grade