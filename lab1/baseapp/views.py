from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db import connection
from .models import Employees, Requests, Request_Employees
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

def delete_employee(request, id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("UPDATE Employees SET status = False WHERE id = %s;", [id])
        return redirect('employee_list')

    # В случае GET запроса, возможно, выполните другие действия, например, показ страницы подтверждения удаления.


def employee_list(request):
    filtered_employees = Employees.objects.filter(status=True)


    filter_param = request.GET.get('filter')
    
    if filter_param:
        filtered_employees = filtered_employees.filter(
            Q(name__icontains=filter_param) | Q(role__icontains=filter_param)
        )
    else:
        filtered_employees = filtered_employees.all()
    
    return render(request, 'employee_list.html', {'employees': filtered_employees})

def employee_detail(request, employee_id):
    try:
        # Получение сотрудника из базы данных
        employee = Employees.objects.get(pk=employee_id)
    except Employees.DoesNotExist:
        return HttpResponse('Сотрудник не найден')

    return render(request, 'employee_detail.html', {'employee': employee})

from .models import Requests, Request_Employees, Employees

def get_last_made_request_employees():
    # Получаем последнюю заявку со статусом 'entered'
    last_made_request = Requests.objects.filter(status='entered').order_by('-created_date').first()

    if last_made_request:
        # Получаем всех сотрудников, связанных с этой заявкой через связующую таблицу и со статусом 'True'
        request_employees = Request_Employees.objects.filter(request=last_made_request, employee__status=True)
        
        employees = []

        for request_employee in request_employees:
            # Получаем дополнительные детали о сотруднике из модели Employees
            employee_details = Employees.objects.get(pk=request_employee.employee.id)
            employees.append(employee_details)
            print(employee_details.photo)

        # Возвращаем последнюю заявку и список сотрудников
        return last_made_request, employees
    else:
        return None, None


def last_made_request_details(request):
    # Получаем последнюю заявку и список сотрудников
    last_made_request, employees = get_last_made_request_employees()

    if last_made_request:
        return render(request, 'request.html', {'last_made_request': last_made_request, 'employees': employees})
    else:
        return render(request, 'request.html', {'error_message': 'Последняя заявка со статусом "made" не найдена.'})


# Employees = [
#         {'title': 'Олег Иванов', 'id': 1, 'photo_url': '/static/man1.jpg', 'other_data': '''Занимал должности инженера по логистике, менеджера проекта по бережливому производству в логистике, менеджера по складской и транспортной логистике, руководителя отдела логистики электронной коммерции.

# Окончил курсы повышения квалификации и имеет многочисленные сертификаты MITx, Supply Chain и Kuehne+Nagel Academy.

# ''', 'role': 'стажер'},
#         {'title': 'Евгений Иванов', 'id': 2, 'photo_url': '/static/man2.jpg', 'other_data': 'Евгений Иванов является кандидатом технических наук по направлению «Теоретические основы информатики», а также магистром техники и технологии по направлению «Системный анализ и управление». Имеет членство в Обществе вычислительного интеллекта (IEEE Computational Intelligence Society).', 'role': 'преподаватель'},
#         {'title': 'Александр Иванов', 'id': 3, 'photo_url': '/static/man3.jpg', 'other_data': 'Помимо преподавательской деятельности занимается фриланс-проектами по программированию, а также работает программистом в Федеральной службе государственной регистрации, кадастра и картографии.', 'role': 'преподаватель'},
#     ]

# def delete_employee(request, id):
#     with connection.cursor() as cursor:
#         cursor.execute("UPDATE Employees SET status = FALSE WHERE id = %s", [id])

#     return redirect('employee_list')

# def employee_list(request):
#     filter_param = request.GET.get('filter')
#     filtered_employees = []

#     if filter_param:
#         for employee in Employees:
#             if filter_param.lower() in employee['title'].lower() or filter_param.lower() in employee['role'].lower():
#                 filtered_employees.append(employee)
#     else:
#         filtered_employees = Employees

#     return render(request, 'employee_list.html', {'employees': filtered_employees})



# def employee_detail(request, employee_id):
#     employee = None
#     for emp in Employees:
#         if emp['id'] == employee_id:
#             employee = emp
#             break

#     if employee is None:
#         return HttpResponse('Сотрудник не найден')

#     return render(request, 'employee_detail.html', {'employee': employee})

