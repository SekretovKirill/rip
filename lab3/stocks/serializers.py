from stocks.models import Employees, Requests, Request_Employees, Users
from rest_framework import serializers
from collections import OrderedDict



class EmployeesSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Employees
        # Поля, которые мы сериализуем
        fields = ["id", "name", "status", "role", "info"]
        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 

class SecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Request_Employees
        fields = ["employee", "security"]
        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 

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
        fields = ["id", "status", "name", "info", "created_date", "formation_date", "completion_date", "client", "moderator"]
        extra_kwargs = {'status': {'required': False}, 'client': {'required': False}} 

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', "name", "email", "role"]