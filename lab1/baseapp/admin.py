from django.contrib import admin
from .models import Employees


class EmployeesAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'status')
    list_filter = ('status', 'role')
    search_fields = ('name', 'role')

admin.site.register(Employees, EmployeesAdmin)

# Register your models here.
