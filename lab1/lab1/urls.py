from django.contrib import admin
from django.urls import path
from baseapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.employee_list, name='employee_list'),
    path('employees/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('employee/delete/<int:id>/', views.delete_employee, name='delete_employee'),
    path('last_made_request_details/', views.last_made_request_details, name='last_made_request_details'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)