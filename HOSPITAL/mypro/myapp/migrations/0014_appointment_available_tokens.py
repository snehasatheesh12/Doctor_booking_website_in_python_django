# Generated by Django 4.2.7 on 2024-09-12 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_remove_appointment_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='available_tokens',
            field=models.PositiveIntegerField(default=10),
        ),
    ]
