# Generated by Django 3.2.13 on 2022-05-21 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipment',
            name='shipment_current_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('sending', 'Sending'), ('received', 'Received')], default='pending', max_length=200),
        ),
    ]
