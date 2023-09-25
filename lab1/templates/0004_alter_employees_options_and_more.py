# Generated by Django 4.2.5 on 2023-09-24 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseapp', '0003_alter_employees_photo'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='employees',
            options={'verbose_name_plural': 'Employees'},
        ),
        migrations.AlterModelOptions(
            name='request_employees',
            options={'verbose_name_plural': 'Request Employees'},
        ),
        migrations.AlterModelOptions(
            name='requests',
            options={'verbose_name_plural': 'Requests'},
        ),
        migrations.AlterModelOptions(
            name='users',
            options={'verbose_name_plural': 'Users'},
        ),
        migrations.AlterField(
            model_name='employees',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='static/'),
        ),
        migrations.AlterModelTable(
            name='employees',
            table='employees',
        ),
        migrations.AlterModelTable(
            name='request_employees',
            table='request_employees',
        ),
        migrations.AlterModelTable(
            name='requests',
            table='requests',
        ),
        migrations.AlterModelTable(
            name='users',
            table='users',
        ),
    ]
