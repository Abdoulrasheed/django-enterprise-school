from django.contrib import admin
from .models import *

class GradeAdmin(admin.ModelAdmin):
	list_display = ['score', 'remark', 'grade', 'total']


class ScoreAdmin(admin.ModelAdmin):
	list_display = ['student', 'mark_percentage', 'subject', 'score']


admin.site.register(Session)
admin.site.register(Batch)
admin.site.register(Section)
admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(Score, ScoreAdmin)
admin.site.register(Student)
admin.site.register(Parent)
admin.site.register(SubjectAllocation)
admin.site.register(Teacher)
admin.site.register(SectionAllocation)
admin.site.register(Grade, GradeAdmin)
admin.site.register(Attendance)
admin.site.register(Notification)
admin.site.register(MarkPercentage)
admin.site.register(FeeType)
admin.site.register(Payment)
admin.site.register(Expense)
admin.site.register(Setting)
admin.site.register(GradeScale)
admin.site.register(EmailMessage)
admin.site.register(ScorePermission)