# Generated by Django 4.1.1 on 2022-09-26 13:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("unity", "0002_visitoremail_delete_email"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="visitoremail",
            name="user",
        ),
    ]
