from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Session)
admin.site.register(Section)
admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(Student)
admin.site.register(Parent)
admin.site.register(SubjectAssign)
admin.site.register(SectionAssign)
admin.site.register(Grade)
admin.site.register(Attendance)
admin.site.register(FeeType)
admin.site.register(Payment)
admin.site.register(Expense)
admin.site.register(Setting)
# Register your models here.
