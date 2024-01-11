from django.db import models

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "users"
        verbose_name_plural = "Users"

class Employees(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    role = models.CharField(max_length=255)
    info = models.CharField(max_length=255, null=True)
    photo = models.ImageField(upload_to='static/', blank=True, null=True)
    photo_binary = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "employees"
        verbose_name_plural = "Employees"

class Requests(models.Model):
    status_choices = (
        ('entered', 'Entered'),
        ('in progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
        ('deleted', 'Deleted'),
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=20, choices=status_choices)
    created_date = models.DateTimeField(auto_now_add=True)
    formation_date = models.DateTimeField(null=True, blank=True, auto_now=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    moderator = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='moderated_requests')
    client = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='client_requests')
    info = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"Request {self.id}"

    class Meta:
        db_table = "requests"
        verbose_name_plural = "Requests"


class Request_Employees(models.Model):
    request = models.ForeignKey(Requests, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    security = models.BooleanField(null=True)

    def __str__(self):
        return f"Request {self.request_id} - Employee {self.employee_id} - Security {self.security}"

    class Meta:
        db_table = "request_employees"
        verbose_name_plural = "Request Employees"
        constraints = [
            models.UniqueConstraint(fields=['request', 'employee'], name='unique_request_employee')
        ]


