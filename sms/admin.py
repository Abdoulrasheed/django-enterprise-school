from django.contrib import admin
from .models import *

class GradeAdmin(admin.ModelAdmin):
	list_display = ['student', 'session', 'term', 'subject', 'remark', 'total']

class UserAdmin(admin.ModelAdmin):
	list_display = ['first_name', 'last_name']

	search_fields = ['first_name', 'last_name']

admin.site.register(User, UserAdmin)
admin.site.register(Session)
admin.site.register(Section)
admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(Student)
admin.site.register(Parent)
admin.site.register(SubjectAssign)
admin.site.register(SectionAssign)
admin.site.register(Grade, GradeAdmin)
admin.site.register(Attendance)
admin.site.register(Notification)
admin.site.register(FeeType)
admin.site.register(Payment)
admin.site.register(Expense)
admin.site.register(Setting)
admin.site.register(GradeScale)
admin.site.register(Sms)
admin.site.register(Ranking)
# Register your models here.
