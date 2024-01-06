from stocks.models import Employees, Requests, Request_Employees
from rest_framework import serializers



class EmployeesSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Employees
        # Поля, которые мы сериализуем
        fields = ["id", "name", "status", "role", "info"]

class SecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Request_Employees
        fields = ["employee", "security"]

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Employees
        # Поля, которые мы сериализуем
        fields = ["id", "name", "status", "role", "info", "photo_binary"]

class RequestsSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Requests
        # Поля, которые мы сериализуем
        fields = ["id", "status", "name", "info", "created_date", "formation_date", "completion_date", "moderator_id"]
