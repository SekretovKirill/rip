"""
URL configuration for lab3 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from stocks import views
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'employees/', views.get_employees, name='stocks-list'),
    path(r'employees/post/', views.post_employees, name='stocks-post'),
    path(r'employees/<int:pk>/', views.get_employees_by_pk, name='stocks-detail'),
    path(r'employees/photo/<int:pk>/', views.get_photo_by_pk, name='stocks-detail'),
    path(r'employees/<int:pk>/put/', views.put_employees, name='stocks-put'),
    path(r'employees/<int:pk>/put_photo/', views.put_photo, name='stocks-put'),
    path(r'employees/<int:pk>/delete/', views.delete_employees, name='stocks-delete'),

    path(r'requests/', views.get_requests, name='stocks-list'),
    # path(r'requests/post/', views.post_requests, name='stocks-post'),
    path(r'requests/<int:pk>/', views.get_requests_by_pk, name='stocks-detail'),
    path(r'requests/<int:pk>/put/', views.put_requests, name='stocks-put'),
    path(r'requests/<int:pk>/put_user/', views.put_requests_user, name='stocks-put'),
    path(r'requests/<int:pk>/put_admin/', views.put_requests_admin, name='stocks-put'),
    path(r'requests/<int:pk>/delete/', views.delete_requests, name='stocks-delete'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path(r'remove-employee-from-request/', views.remove_employee_from_request, name='remove-employee-from-request'),
    path(r'requests-for-employee/<int:employee_id>/', views.requests_for_employee, name='requests-for-employee'),
    path(r'add-employee-to-request/<int:pk>/', views.add_employee_to_request, name='add-employee-to-request'),

    path('admin/', admin.site.urls),
]