# Generated by Django 4.2.7 on 2024-09-10 10:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_myadmin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myadmin',
            name='status',
        ),
    ]
