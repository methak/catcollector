# Generated by Django 3.2.7 on 2021-09-13 21:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_alter_feeding_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='feeding',
            options={'ordering': ['-date']},
        ),
    ]
