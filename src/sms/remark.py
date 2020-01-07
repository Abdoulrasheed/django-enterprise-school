from utils.constants import *
from .models import GradeScale

def getRemark(total, section):
	gradeScale = GradeScale.objects.filter(section=section)
	for i in gradeScale:
		if total in range(i.mark_from, i.mark_upto+1):
			return i.remark

# def getGrade(total):
# 	gradeScale = GradeScale.objects.all()
# 	for i in gradeScale:
# 		if total in range(i.mark_from, i.mark_upto+1):
# 			return i.grade

def get_grade(total, section):
	gradeScale = GradeScale.objects.filter(section=section)
	if total == None:
		return [None, None]
	for i in gradeScale:
		if i.mark_from <= total <= i.mark_upto:
			return [i.grade, i.remark]

def getGradeWithTotalApproximate(total):
	total = round(total, 0)
	gradeScale = GradeScale.objects.all()
	for i in gradeScale:
		if total in range(i.mark_from, i.mark_upto+1):
			return i.grade