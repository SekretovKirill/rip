from django.contrib import admin
from .models import Employees, Users, Requests, Request_Employees


class EmployeesAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'status')
    list_filter = ('status', 'role')
    search_fields = ('name', 'role')

admin.site.register(Employees, EmployeesAdmin)
admin.site.register(Requests)
admin.site.register(Users)
admin.site.register(Request_Employees)
# Register your models here.
