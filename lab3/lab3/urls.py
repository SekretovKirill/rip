from django.contrib import admin
from stocks import views
from django.urls import include, path
from rest_framework import routers
from rest_framework import permissions
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()
schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

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
   #  path(r'requests-for-employee/<int:employee_id>/', views.requests_for_employee, name='requests-for-employee'),
    path(r'add-employee-to-request/<int:pk>/', views.add_employee_to_request, name='add-employee-to-request'),

    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('auth/register',  views.register, name='register'),
    path('auth/login',  views.login, name='login'),
    path('auth/logout', views.logout, name='logout'),

    path(r'put_security/<int:employee_id>/<int:request_id>/', views.put_security, name='put-security'),
    path(r'send_security/<int:employee_id>/<int:request_id>/', views.send_security, name='send_security'),
    
]