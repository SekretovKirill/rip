import ast
from operator import itemgetter
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from stocks.serializers import EmployeesSerializer, RequestsSerializer, PhotoSerializer
from stocks.models import Employees, Requests, Request_Employees, Users
from rest_framework.decorators import api_view
from django.db.models import Q
from datetime import datetime
from io import BytesIO
from PIL import Image

def image_to_binary(image_data):
    image = Image.open(BytesIO(image_data))
    image_binary = BytesIO()
    image.save(image_binary, format="JPEG")
    return image_binary.getvalue()

# def binary_to_image(binary_data):
#     # Преобразуем бинарные данные в изображение
#     image = Image.open(BytesIO(binary_data))
#     return image


@api_view(['PUT'])
def put_photo(request, pk, format=None):    
    """
    Добавляет новую акцию
    """
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

@api_view(["GET"])
def get_photo_by_pk(request, pk):
    if not Employees.objects.filter(pk=pk).exists():
        return Response(f"Сотрудника с таким id не существует!")

    employee = Employees.objects.get(pk=pk)
    serializer = PhotoSerializer(employee)

    return Response(serializer.data)

@api_view(['Get'])
def get_employees(request, format=None):
    filter_param = request.GET.get('filter')
    if filter_param:
        employees = Employees.objects.filter(
            Q(name__icontains=filter_param) | Q(role__icontains=filter_param)
        ).filter(status=True)
    else:
        employees = Employees.objects.filter(status=True)

    serializer = EmployeesSerializer(employees, many=True)

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



@api_view(['Post'])
def post_employees(request, format=None):    
    """
    Добавляет новую акцию
    """
    print('post')
    serializer = EmployeesSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Put'])
def put_employees(request, pk, format=None):
    """
    Обновляет информацию об акции
    """
    stock = get_object_or_404(Employees, pk=pk)
    serializer = EmployeesSerializer(stock, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Delete'])
def delete_employees(request, pk, format=None):    
    """
    Удаляет информацию об акции
    """
    group = Employees.objects.get(pk=pk)
    if group.status == False:
        return Response(f"Employee с id {pk} не существует!", status=404)
    group.status = False
    group.save()
    groups = Employees.objects.filter(status=True)
    serializer = EmployeesSerializer(groups, many=True)
    return Response(serializer.data)




@api_view(['Get'])
def get_requests(request, format=None):
        # Получаем все заявки, которые не были удалены
    requests = Requests.objects.exclude(status='deleted')

    # Инициализируем пустой список для хранения конечных данных ответа
    response_data = []

    for request in requests:
        # Получить связанных сотрудников для текущей заявки
        request_employees = Request_Employees.objects.filter(request=request)

        # Инициализируем список данных о сотрудниках
        employee_data = []

        for request_employee in request_employees:
            # Получить связанные с сотрудником данные
            employee = request_employee.employee
            employee_data.append({
                "employee": EmployeesSerializer(employee).data
            })

        request_data = RequestsSerializer(request).data
        response_data.append({
            "request": request_data,
            "related_employees": employee_data
        })

    return Response(response_data)

@api_view(["GET"])
def get_requests_by_pk(request, pk):
    try:
        request = Requests.objects.get(pk=pk)
        employees = Request_Employees.objects.filter(request=request)
        employee_ids = employees.values_list("employee", flat=True)
        related_employees = Employees.objects.filter(id__in=employee_ids, status=True)
        
        # Сериализация заявки
        request_serializer = RequestsSerializer(request)
        
        # Сериализация связанных сотрудников
        employees_serializer = EmployeesSerializer(related_employees, many=True)
        
        # Добавление информации о сотрудниках к информации о заявке
        request_data = request_serializer.data
        request_data["related_employees"] = employees_serializer.data
        
        return Response(request_data)
    except Requests.DoesNotExist:
        return Response(f"Запроса с id {pk} не существует!", status=404)


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
@api_view(['PUT'])
def put_requests(request, pk, format=None):
    if not Requests.objects.filter(pk=pk).exists():
        return Response(f"Запроса с таким id не существует!")
    if 'Status' in request.data:
        return Response({'error': 'Нельзя изменять статус через это представление'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = RequestsSerializer(request, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                    
@api_view(['Put'])
def put_requests_user(request, pk, format=None):
    if not Requests.objects.filter(pk=pk).exists():
        return Response(f"Запроса с таким id не существует!")
    request_obj = get_object_or_404(Requests, pk=pk)
    request_status = request.data.get("status")
    if request_status in ['entered']:
        request_obj.Status = request_status
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
        return Response({"detail": "Invalid status. Use 'in progress' or 'completed' or 'canceled'"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def put_requests_admin(request, pk, format=None):
    status_choices = ['in progress', 'completed', 'canceled']
    if not Requests.objects.filter(pk=pk).exists():
        return Response(f"Запроса с таким id не существует!")
    request_obj = get_object_or_404(Requests, pk=pk)
    request_status = request.data.get("status")
    if request_status in status_choices:
        if request_status in ["completed"]:
            request_obj.completion_date = datetime.now()
        request_obj.Status = request_status
        request_obj.formation_date = datetime.now()
        request_obj.save()
        serializer = RequestsSerializer(request_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"detail": "Invalid status. Use 'in progress' or 'completed' or 'canceled'"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['Delete'])
def delete_requests(request, pk, format=None):    
    if not Requests.objects.filter(pk=pk).exists():
        return Response(f"Запроса с таким id не существует!")
    group = Requests.objects.get(pk=pk)
    if group.status == 'deleted':
        return Response(f"Запроса с id {pk} не существует!", status=404)
    group.status = 'deleted'
    group.save()
    groups = Requests.objects.exclude(status='deleted')
    serializer = RequestsSerializer(groups, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def add_employee_to_request(request, pk, format=None):
    name = request.data.get('name')
    info = request.data.get('info')
    try:
        request_instance = Requests.objects.get(moderator = Users.objects.get(id=1), status="entered")
    except Requests.DoesNotExist:
        request_instance = Requests.objects.create(moderator = Users.objects.get(id=1), status='entered', name = name, info = info, created_date = datetime.now())
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
    
@api_view(['GET'])
def requests_for_employee(request, employee_id):
    try:
        employee_instance = Employees.objects.get(id=employee_id)

        requests = Request_Employees.objects.filter(employee=employee_instance).values_list('request', flat=True)

        requests_data = Requests.objects.filter(id__in=requests).exclude(status='deleted')
        requests_serializer = RequestsSerializer(requests_data, many=True)

        return Response(requests_serializer.data, status=status.HTTP_200_OK)
    except Employees.DoesNotExist:
        return Response({"message": "Сотрудник не найден"}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['DELETE'])
def remove_employee_from_request(request):
    request_id = request.data.get('request_id')
    employee_id = request.data.get('employee_id')

    try:
        request_instance = Requests.objects.get(id=request_id)
        employee_instance = Employees.objects.get(id=employee_id)
        if not Request_Employees.objects.filter(request=request_instance, employee=employee_instance):
            return Response({"message": "Связь не найдена"}, status=status.HTTP_404_NOT_FOUND)
        Request_Employees.objects.filter(request=request_instance, employee=employee_instance).delete()

        return Response({"message": "Сотрудник успешно удален из заявки"}, status=status.HTTP_200_OK)
    except (Requests.DoesNotExist, Employees.DoesNotExist):
        return Response({"message": "Заявка или сотрудник не найдены"}, status=status.HTTP_404_NOT_FOUND)