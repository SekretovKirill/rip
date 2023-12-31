from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db import connection
from datetime import date

# Пропуски на выходные и праздничные дни. Услуги - список сотрудников, заявки - заявка на работу в выходной, праздничный или ночью с указанием причины.

def hello(request):
    return render(request, 'index.html', { 'data' : {
        'current_date': date.today(),
        'list': ['python', 'django', 'html']
    }})

employees = [
        {'title': 'Олег Иванов', 'id': 1, 'photo_url': '/static/man1.jpg', 'other_data': '''Занимал должности инженера по логистике, менеджера проекта по бережливому производству в логистике, менеджера по складской и транспортной логистике, руководителя отдела логистики электронной коммерции.

Окончил курсы повышения квалификации и имеет многочисленные сертификаты MITx, Supply Chain и Kuehne+Nagel Academy.

''', 'role': 'стажер'},
        {'title': 'Евгений Иванов', 'id': 2, 'photo_url': '/static/man2.jpg', 'other_data': 'Евгений Иванов является кандидатом технических наук по направлению «Теоретические основы информатики», а также магистром техники и технологии по направлению «Системный анализ и управление». Имеет членство в Обществе вычислительного интеллекта (IEEE Computational Intelligence Society).', 'role': 'преподаватель'},
        {'title': 'Александр Иванов', 'id': 3, 'photo_url': '/static/man3.jpg', 'other_data': 'Помимо преподавательской деятельности занимается фриланс-проектами по программированию, а также работает программистом в Федеральной службе государственной регистрации, кадастра и картографии.', 'role': 'преподаватель'},
    ]

def delete_employee(request, id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE Employees SET status = FALSE WHERE id = %s", [id])

    return redirect('employee_list')

def employee_list(request):
    filter_param = request.GET.get('filter')
    filtered_employees = []

    if filter_param:
        for employee in employees:
            if filter_param.lower() in employee['title'].lower() or filter_param.lower() in employee['role'].lower():
                filtered_employees.append(employee)
    else:
        filtered_employees = employees

    return render(request, 'employee_list.html', {'employees': filtered_employees})



def employee_detail(request, employee_id):
    employee = None
    for emp in employees:
        if emp['id'] == employee_id:
            employee = emp
            break

    if employee is None:
        return HttpResponse('Сотрудник не найден')

    return render(request, 'employee_detail.html', {'employee': employee})

def GetOrder(request, id):
    return render(request, 'order.html', {'data' : {
        'current_date': date.today(),
        'id': id
    }})

def sendText(request):
    input_text = request.POST['text']