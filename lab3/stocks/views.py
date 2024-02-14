import ast
import requests
from operator import itemgetter
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework import status
from stocks.serializers import EmployeesSerializer, RequestsSerializer, PhotoSerializer, SecuritySerializer, UsersSerializer
from stocks.models import Employees, Requests, Request_Employees, Users
from stocks.redis_views import (set_key, get_value, delete_value)
from rest_framework.decorators import api_view
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime
from io import BytesIO
from PIL import Image
from drf_yasg import openapi
import hashlib
import secrets
from django.utils.dateparse import parse_date
import requests
from django.middleware import csrf
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from jose import jwt
from django.conf import settings



#-----------------------------auth-------------------------------
def check_authorize(request):
    existing_session = request.COOKIES.get('session_key')
    # existing_session = request.headers.get('Authorization', '').split('Bearer ')[-1]
    print(existing_session)
    if existing_session and get_value(existing_session):
        user_id = get_value(existing_session)
        try:
            user = Users.objects.get(id=user_id)
            return user
        except Users.DoesNotExist:
            pass
    return None

# def check_authorize(request):
#     token = request.headers.get('Authorization', '').split('Bearer ')[-1]
#     if token:
#         try:
#             payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
#             user_id = payload.get('user_id')
#             user = Users.objects.get(id=user_id)
#             return user
#         except (jwt.JWTError, Users.DoesNotExist):
#             pass

#     return None

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'password', 'name'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING),
        'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    responses={
        201: 'Пользователь успешно создан',
        400: 'Не хватает обязательных полей или пользователь уже существует',
    },
    operation_summary='Регистрация нового пользователя'
)
@api_view(['POST'])
def register(request, format=None):
    required_fields = ['email', 'name', 'password']
    missing_fields = [field for field in required_fields if field not in request.data]

    if missing_fields:
        return Response({'Ошибка': f'Не хватает обязательных полей: {", ".join(missing_fields)}'}, status=status.HTTP_400_BAD_REQUEST)

    if Users.objects.filter(email=request.data['email']).exists() or Users.objects.filter(name=request.data['name']).exists():
        return Response({'Ошибка': 'Пользователь с таким email или username уже существует'}, status=status.HTTP_400_BAD_REQUEST)

    password_hash = make_password(request.data["password"])

    Users.objects.create(
        email=request.data['email'],
        name=request.data['name'],
        password=password_hash,
        role='User',
    )
    return Response({'Пользователь успешно зарегистрирован'},status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'password'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING),
        'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
        },
    ),
    responses={
        200: 'Успешная авторизация', 
        400: 'Неверные параметры запроса или отсутствуют обязательные поля',
        401: 'Неавторизованный доступ',
    },
    operation_summary='Метод для авторизации'
)
@api_view(['POST'])
def login(request, format=None):
    existing_session = request.COOKIES.get('session_key')
    # print(1)
    # existing_session = request.headers.get('Authorization', '').split('Bearer ')[-1]
    print(existing_session)

    if existing_session and get_value(existing_session):
        return Response({'User_id': get_value(existing_session)})

    email = request.data.get("email")
    password = request.data.get("password")
    
    if not email or not password:
        return Response({'error': 'Необходимы почта и пароль'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = Users.objects.get(email=email)
    except Users.DoesNotExist:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if check_password(password, user.password):
        random_part = secrets.token_hex(8)
        session_hash = hashlib.sha256(f'{user.id}:{email}:{random_part}'.encode()).hexdigest()
        set_key(session_hash, user.id)

        serialize = UsersSerializer(user)
        serialized_data = serialize.data
        serialized_data['session_key'] = session_hash

        response = Response(serialized_data)
        response.set_cookie('session_key', session_hash, max_age=86400)
        return response

    return Response(status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(
    method='get',
    responses={
        200: 'Успешный выход',
        401: 'Неавторизованный доступ',
    },
    operation_summary='Метод для выхода пользователя из системы'
)
@api_view(['GET'])
def logout(request):
    session_key = request.COOKIES.get('session_key')

    if session_key:
        if not get_value(session_key):
            return Response({'error': 'Вы не авторизованы'}, status=status.HTTP_401_UNAUTHORIZED)
        delete_value(session_key)
        response = Response({'message': 'Вы успешно вышли из системы'})
        response.delete_cookie('session_key')
        return response
    else:
        return Response({'error': 'Вы не авторизованы'}, status=status.HTTP_401_UNAUTHORIZED)

#------------------------------------------------------------
def image_to_binary(image_data):
    image = Image.open(BytesIO(image_data))
    image_binary = BytesIO()
    image.save(image_binary, format="JPEG")
    return image_binary.getvalue()

@swagger_auto_schema(
    method='put',
    operation_summary="Добавляет новую фотографию сотруднику",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['name', 'status', 'role', 'info'],
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING),
            'status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            'role': openapi.Schema(type=openapi.TYPE_STRING),
            'info': openapi.Schema(type=openapi.TYPE_STRING),
            'photo_binary': openapi.Schema(type=openapi.TYPE_FILE),
        },
    ),
    responses={201: PhotoSerializer},
    consumes=['multipart/form-data']
)
@api_view(['PUT'])
def put_photo(request, pk, format=None): 
    user = check_authorize(request)
    if not user:
        return Response({'error': 'необходима авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
    elif not (user.role == 'Admin'):
        return Response({'error': 'недостаточно прав'}, status=status.HTTP_403_FORBIDDEN)
       
    stock = get_object_or_404(Employees, pk=pk)
    image_binary = None
    if 'photo_binary' in request.data:
        image_data = request.data.pop('photo_binary')[0].read()
        image_binary = image_to_binary(image_data)
    else:
        print(0)
    
    serializer = PhotoSerializer(stock, data=request.data)
    if serializer.is_valid():
        if image_binary:
            serializer.save(photo_binary=image_binary)
        else:
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='get', operation_summary="Возвращает фото сотрудника", responses={200: PhotoSerializer(many=True)})
@api_view(["GET"])
def get_photo_by_pk(request, pk):
    if not Employees.objects.filter(pk=pk).exists():
        return Response(f"Сотрудника с таким id не существует!")

    employee = Employees.objects.get(pk=pk)
    serializer = PhotoSerializer(employee)

    return Response(serializer.data)

@swagger_auto_schema(method='get', operation_summary="Возвращает список сотрудников", responses={200: PhotoSerializer(many=True)})
@api_view(['Get'])
def get_employees(request, format=None):
    filter_param = request.GET.get('filter')
    if filter_param:
        employees = Employees.objects.filter(
            Q(name__icontains=filter_param) | Q(role__icontains=filter_param)
        ).filter(status=True)
    else:
        employees = Employees.objects.filter(status=True)
    user = check_authorize(request)
    if user and user.role == 'User':
        draft = Requests.objects.filter(client=user, status='entered').first()
        if draft:
            # Если у пользователя есть активная заявка, добавьте ее данные перед списком событий
            employees_data = PhotoSerializer(employees, many=True).data
            response_data = {'employees': employees_data, 'draft_id': draft.id}
            return Response(response_data)
        else:
            employees_data = PhotoSerializer(employees, many=True).data
            response_data = {'employees': employees_data, 'draft_id': None}
            return Response(response_data)
    else:
        employees_data = PhotoSerializer(employees, many=True).data
        response_data = {'employees': employees_data, 'draft_id': None}
        return Response(response_data)

    serializer = PhotoSerializer(employees, many=True)

    return Response(serializer.data)


    # employees = Employees.objects.filter(status=True)
    # serializer = EmployeesSerializer(employees, many=True)
    # return Response(serializer.data)

# @api_view(["GET"])
# def search_employees(request):
#     filter_param = request.GET.get('filter')
#     if filter_param:
#         employees = Employees.objects.filter(
#             Q(name__icontains=filter_param) | Q(role__icontains=filter_param)
#         ).filter(status=True)
#     else:
#         employees = Employees.objects.filter(status=True)
#     serializer = EmployeesSerializer(employees, many=True)

#     return Response(serializer.data)

@swagger_auto_schema(method='get', operation_summary="Возвращает информацию о сотруднике", responses={200: EmployeesSerializer()})
@api_view(["GET"])
def get_employees_by_pk(request, pk):
    if not Employees.objects.filter(pk=pk).exists():
        return Response(f"Сотрудника с таким id не существует!")

    employee = Employees.objects.get(pk=pk)
    # save = None
    # if employee.photo_binary and False:
    #     save = employee.photo_binary
    #     employee.photo_binary = binary_to_image(employee.photo_binary)
    #     serializer = EmployeesSerializer(employee)
    #     employee.photo_binary = save
    # else:
    serializer = EmployeesSerializer(employee)

    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    operation_summary="Добавляет нового сотрудника",
    request_body=EmployeesSerializer,
    responses={201: 'Created', 400: 'Bad Request'}
)
@api_view(['Post'])
def post_employees(request, format=None):
    user = check_authorize(request)
    if not user:
        return Response({'error': 'необходима авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
    elif not (user.role == 'Admin'):
        return Response({'error': 'недостаточно прав'}, status=status.HTTP_403_FORBIDDEN)
    if 'photo_binary' in request.data:
        image_data = request.data.pop('photo_binary')[0].read()
        image_binary = image_to_binary(image_data)
        serializer = PhotoSerializer(data=request.data)
    else:
        serializer = EmployeesSerializer(data=request.data)
    
    if serializer.is_valid():
        if 'photo_binary' in request.data:
            serializer.save(photo_binary=image_binary)
        else:
            serializer.save()
        ser_data=serializer.data
        ser_data.status=True
        return Response(ser_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='put',
    operation_summary="Обновляет информацию о сотруднике",
    request_body=EmployeesSerializer,
    responses={200: 'OK', 400: 'Bad Request'}
)
@api_view(['Put'])
def put_employees(request, pk, format=None):
    user = check_authorize(request)
    if not user:
        return Response({'error': 'необходима авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
    if not user.role == 'Admin':
        return Response({'error': 'необходима авторизация за администратора'}, status=status.HTTP_403_FORBIDDEN)
    stock = get_object_or_404(Employees, pk=pk)
    serializer = EmployeesSerializer(stock, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @require_http_methods(["DELETE", "OPTIONS"])
# @csrf_exempt
@swagger_auto_schema(
    method='delete',
    operation_summary="Удаляет информацию о сотруднике",
    responses={200: 'OK', 404: 'Not Found'}
)
# @require_http_methods(["DELETE"])
# @csrf_exempt
@api_view(['delete'])
def delete_employees(request, pk, format=None):    
    user = check_authorize(request)
    if not (user and user.role == 'Admin'):
        return Response({'error': 'необходима авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
    elif(user.role == 'User'):
        return Response({'error': 'недостаточно прав'}, status=status.HTTP_403_FORBIDDEN)
    group = Employees.objects.get(pk=pk)
    if group.status == False:
        return Response(f"Employee с id {pk} не существует!", status=404)
    group.status = False
    group.save()
    groups = Employees.objects.filter(status=True)
    serializer = EmployeesSerializer(groups, many=True)
    # response = HttpResponse()
    # response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    # response['Access-Control-Allow-Methods'] = 'DELETE, GET, OPTIONS, PATCH, POST, PUT'
    # response['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, Z-Key'
    # response['Access-Control-Allow-Credentials'] = 'true'
    return Response(serializer.data)

#---------------------------------------------------------------------
@swagger_auto_schema(
    method='get',
    operation_summary="Возвращает список всех заявок с сотрудниками",
    responses={200: 'OK'}
)
@api_view(['GET'])
def get_requests(request, format=None):
    # Получаем все заявки, которые не были удалены
    user = check_authorize(request)
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    Status = request.query_params.get('status')
    if not user:
        return Response({'error': 'необходима авторизация'}, status=status.HTTP_401_UNAUTHORIZED)

    if user.role == 'Admin':
        requests = Requests.objects.exclude(status__in=['deleted', 'entered'])
    elif user.role == 'User':
        requests = Requests.objects.exclude(status__in=['deleted', 'entered'])
    if start_date:
        start_date = parse_date(start_date)
        requests = requests.filter(formation_date__gte=start_date)
    if end_date:
        end_date = parse_date(end_date)
        requests = requests.filter(formation_date__lte=end_date)
    if Status:
        requests = requests.filter(status=Status)
    
    # Инициализируем пустой список для хранения конечных данных ответа
    response_data = []

    for request in requests:
        # Получить связанных сотрудников для текущей заявки
        request_employees = Request_Employees.objects.filter(request=request)

        # Инициализируем список данных о сотрудниках
        employee_data = []

        # Переменная для подсчета количества True значений поля security
        true_security_count = 0

        for request_employee in request_employees:
            # Получить связанные с сотрудником данные
            employee = request_employee.employee
            
            # Сериализация сотрудника с учетом поля security
            employee_serializer = EmployeesSerializer(employee)
            security_info = Request_Employees.objects.get(request=request, employee=employee).security
            employees_data = employee_serializer.data
            employees_data["security"] = security_info
            employee_data.append({
                "employee": employees_data
            })

            # Подсчет True значений поля security
            if security_info == True or security_info == False:
                true_security_count += 1

        # Добавление количества True security полей к заявке
        request_data = RequestsSerializer(request).data
        request_data["security_count"] = true_security_count

        response_data.append({
            "request": request_data,
            "related_employees": employee_data
        })

    return Response(response_data)



@swagger_auto_schema(
    method='get',
    operation_summary="Возвращает информацию о заявке и связанных сотрудниках",
    responses={200: RequestsSerializer}
)
@api_view(["GET"])
def get_requests_by_pk(request, pk):
    user = check_authorize(request)
    if not user:
        return Response({'error': 'необходима авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        request = Requests.objects.get(pk=pk)
    except Requests.DoesNotExist:
        return Response({'error': 'Заявка с указанным ID не существует'}, status=status.HTTP_404_NOT_FOUND)

    if user.role == 'Admin' or user == request.client:
        try:
            
            employees = Request_Employees.objects.filter(request=request)
            employee_ids = employees.values_list("employee", flat=True)
            related_employees = Employees.objects.filter(id__in=employee_ids, status=True)
            related_req_emp = Request_Employees.objects.filter(employee__in=employee_ids, request=pk)
            
            # Сериализация заявки
            request_serializer = RequestsSerializer(request)
            
            # Сериализация связанных сотрудников
            employees_serializer = PhotoSerializer(related_employees, many=True)

            req_emp_serializer = SecuritySerializer(related_req_emp, many=True)
            request_data = request_serializer.data
            employees_data = employees_serializer.data
            for employee_data in employees_data:
                security_info = next((item["security"] for item in req_emp_serializer.data if item["employee"] == employee_data["id"]), None)
                employee_data["security"] = security_info
            request_data["related_employees"] = employees_data
            
            return Response(request_data)
        except Requests.DoesNotExist:
            return Response(f"Запроса с id {pk} не существует!", status=404)
    else:
        return Response({'error': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

# @api_view(['Post'])
# def post_requests(request, format=None):    
#     """
#     Добавляет новую акцию
#     """
#     print('post')
#     serializer = RequestsSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


status_choices = (
        ('entered', 'Entered'),
        ('in progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
        ('deleted', 'Deleted'),
    )
@swagger_auto_schema(
    method='put',
    operation_summary="Обновляет информацию о заявке",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING),
            'info': openapi.Schema(type=openapi.TYPE_STRING),
            'moderator_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'created_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
            'formation_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
            'completion_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        },
    ),
    responses={200: 'OK', 400: 'Bad Request'}
)
@api_view(['PUT'])
def put_requests(request, pk, format=None):
    user = check_authorize(request)
    if not user:
        return Response({'error': 'необходима авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
    if not Requests.objects.filter(pk=pk).exists():
        return Response(f"Запроса с таким id не существует!")
    if 'status' in request.data:
        return Response({'error': 'Нельзя изменять статус через это представление'}, status=status.HTTP_400_BAD_REQUEST)
    request_obj = get_object_or_404(Requests, pk=pk)
    request_obj.status = request_obj.status
    request_obj.formation_date = datetime.now()
    request_obj.save()
    serializer = RequestsSerializer(request_obj, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='put',
    operation_summary="Обновляет информацию о заявке от пользователя",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_STRING),
        },
    required=['status']
    ),
    responses={200: 'OK', 400: 'Bad Request'}
)
@api_view(['Put'])
def put_requests_user(request, pk, format=None):
    user = check_authorize(request)
    if not user:
        return Response({'error': 'необходима авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
    elif not (user.role == 'User'):
        return Response({'error': 'недостаточно прав'}, status=status.HTTP_403_FORBIDDEN)
    
    if not Requests.objects.filter(pk=pk).exists():
        return Response(f"Запроса с таким id не существует!")
    request_obj = get_object_or_404(Requests, pk=pk)
    if request_obj.client != user:
        return Response({'error': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
    if request_obj.status != "entered":
        return Response({"detail": "Заявка не является черновиком"}, status=status.HTTP_400_BAD_REQUEST)
    request_status = 'in progress'
    if request_status in ['in progress']:
        request_obj.status = request_status
        request_obj.formation_date = datetime.now()
        request_obj.save()

        serializer = RequestsSerializer(request_obj)
        serializer = RequestsSerializer(request_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"detail": "Неверный статус. Используйте 'in progress'"}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='put',
    operation_summary="Обновляет информацию о заявке от администратора",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_STRING),
        },
    required=['status']
    ),
    responses={200: 'OK', 400: 'Bad Request'}
)
@csrf_exempt
@api_view(['PUT'])
def put_requests_admin(request, pk, format=None):
    user = check_authorize(request)
    if not user:
        return Response({'error': 'необходима авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
    elif not (user.role == 'Admin'):
        return Response({'error': 'недостаточно прав'}, status=status.HTTP_403_FORBIDDEN)
    status_choices = ['completed', 'canceled']
    if not Requests.objects.filter(pk=pk).exists():
        return Response(f"Запроса с таким id не существует!")
    request_obj = get_object_or_404(Requests, pk=pk)
    request_status = request.data.get("status")
    if request_obj.status != 'in progress':
        print(request_obj.status)
        return Response({"detail": "Заявка не в работе"}, status=status.HTTP_400_BAD_REQUEST)
    
    if request_status in status_choices:
        if request_status in ["completed"]:
            request_obj.completion_date = datetime.now()
        request_obj.status = request_status
        request_obj.formation_date = datetime.now()
        user_instance = Users.objects.get(pk=user.id)  # Получаем объект пользователя по его id
        request_obj.moderator = user_instance  # Присваиваем объект пользователя полю moderator
        request_obj.save()  # Сохраняем изменения
        serializer = RequestsSerializer(request_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = Response(serializer.data)
        else:
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        response = Response({"detail": "Неверный статус. Используйте 'completed' или 'canceled'"}, status=status.HTTP_400_BAD_REQUEST)
    
    return response

@swagger_auto_schema(
    method='delete',
    operation_summary="Удаляет заявку",
    responses={200: 'OK', 404: 'Not Found'}
)
@api_view(['Delete'])
def delete_requests(request, pk, format=None): 
    user = check_authorize(request)
    if not (user):
        return Response({'error': 'Необходима авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
    elif (user.role == 'Admin'):
        return Response({'error': 'Только пользователь может удалить сотрудника из заявки'}, status=status.HTTP_403_FORBIDDEN)
    if not Requests.objects.filter(pk=pk).exists():
        return Response(f"Запроса с таким id не существует!")
    group = Requests.objects.get(pk=pk)
    if group.client != user:
        return Response({'error': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

    if group.status == 'deleted':
        return Response(f"Запроса с id {pk} не существует!", status=404)
    group.status = 'deleted'
    group.save()
    groups = Requests.objects.exclude(status='deleted')
    serializer = RequestsSerializer(groups, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='post',
    operation_summary="Добавляет сотрудника к заявке",
    responses={201: 'Created', 404: 'Not Found'}
)
@api_view(['POST'])
def add_employee_to_request(request, pk, format=None):
    user = check_authorize(request)
    if not (user):
        return Response({'error': 'необходима авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
    elif (user.role == 'Admin'):
        return Response({'error': 'Только пользователь может удалить сотрудника из заявки'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        request_instance = Requests.objects.get(status="entered", client = user)
    except Requests.DoesNotExist:
        request_instance = Requests.objects.create(status='entered', created_date = datetime.now(), name='Заявка', client_id=user.id)
        request_instance.save()

    try:
        employee_instance = Employees.objects.get(id=pk)

        # Создайте связь в таблице Request_Employees
        request_employee = Request_Employees(request=request_instance, employee=employee_instance)
        request_employee.save()

        # Сериализуем сотрудника и заявку
        employee_serializer = EmployeesSerializer(employee_instance)
        request_serializer = RequestsSerializer(request_instance)


        return Response({
            "message": "Сотрудник успешно добавлен к заявке",
            "employee": employee_serializer.data,
            "request": request_serializer.data
        }, status=status.HTTP_201_CREATED)
    except Employees.DoesNotExist:
        return Response({"message": "Сотрудник не найден"}, status=status.HTTP_404_NOT_FOUND)

# @swagger_auto_schema(
#     method='get',
#     operation_summary="Возвращает заявки для сотрудника",
#     responses={200: RequestsSerializer(many=True), 404: 'Not Found'}
# )
# @api_view(['GET'])
# def requests_for_employee(request, employee_id):
#     try:
#         employee_instance = Employees.objects.get(id=employee_id)

#         requests = Request_Employees.objects.filter(employee=employee_instance).values_list('request', flat=True)

#         requests_data = Requests.objects.filter(id__in=requests).exclude(status='deleted')
#         requests_serializer = RequestsSerializer(requests_data, many=True)

#         return Response(requests_serializer.data, status=status.HTTP_200_OK)
#     except Employees.DoesNotExist:
#         return Response({"message": "Сотрудник не найден"}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='delete',
    operation_summary="Удаляет сотрудника из заявки",
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'request_id': openapi.Schema(type=openapi.TYPE_STRING),
                'employee_id': openapi.Schema(type=openapi.TYPE_STRING),
            },
        required=['request_id', 'employee_id']
        ),
    responses={200: 'OK', 404: 'Not Found'}
)
@api_view(['delete'])
def remove_employee_from_request(request):
    user = check_authorize(request)
    if not (user):
        return Response({'error': 'необходима авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
    elif (user.role == 'Admin'):
        return Response({'error': 'Только пользователь может удалить сотрудника из заявки'}, status=status.HTTP_403_FORBIDDEN)
    request_id = request.data.get('request_id')
    employee_id = request.data.get('employee_id')

    try:
        request_instance = Requests.objects.get(id=request_id)
        if request_instance.client != user:
            return Response({'error': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

        employee_instance = Employees.objects.get(id=employee_id)
        if not Request_Employees.objects.filter(request=request_instance, employee=employee_instance):
            return Response({"message": "Связь не найдена"}, status=status.HTTP_404_NOT_FOUND)
        Request_Employees.objects.filter(request=request_instance, employee=employee_instance).delete()

        return Response({"message": "Сотрудник успешно удален из заявки"}, status=status.HTTP_200_OK)
    except (Requests.DoesNotExist, Employees.DoesNotExist):
        return Response({"message": "Заявка или сотрудник не найдены"}, status=status.HTTP_404_NOT_FOUND)
    
# ############################  async service  ##############################################

@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['security_value', 'key'],
        properties={
            'security_value': openapi.Schema(type=openapi.TYPE_STRING),
            'key': openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    responses={200: 'OK', 404: 'Not Found'},
    operation_summary="Обновляет информацию о безопасности сотрудника в заявке"
)
@api_view(['PUT'])
def put_security(request, employee_id,request_id):
    security_value = request.data.get('security_value')
    key = request.data.get('key')
    if key != 'Psq958lBV':
        return Response({"error": "Ключ неверен"}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        try:
            target_request = Requests.objects.get(id=request_id)
            target_employee = Employees.objects.get(id=employee_id)

            req_emp_list = Request_Employees.objects.filter(request=target_request, employee=target_employee)

            with transaction.atomic():
                req_emp_list.update(security=security_value)

            return Response({"security": security_value}, status=status.HTTP_200_OK)

        except Requests.DoesNotExist:
            return Response({"error": "Заявка не найдена"}, status=status.HTTP_404_NOT_FOUND)

        except Employees.DoesNotExist:
            return Response({"error": "Сотрудник не найден"}, status=status.HTTP_404_NOT_FOUND)

        except Request_Employees.DoesNotExist:
            return Response({"error": "Связь не найдена"}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='post',
    responses={200: 'OK', 500: 'Internal Server Error'},
    operation_summary="Отправляет запрос на безопасность"
)
@api_view(['POST'])
def send_security(request, request_id, employee_id):
    data = {
        'employee_id': employee_id,
        'request_id': request_id,
    }

    try:
        response = requests.post('http://192.168.43.241:8080/check/', data=data)

        if response.status_code == 200:
            return Response({'message': 'Запрос успешно отправлен'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Не удалось отправить запрос. Статус ответа: {}'.format(response.status_code)}, status=500)
    except Exception as e:
        return Response({'error': 'Error: {}'.format(str(e))}, status=500)
    
