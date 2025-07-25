# Generated by Django 5.0.14 on 2025-07-07 08:55

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_specialorder'),
    ]

    operations = [
        migrations.CreateModel(
            name='MealSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Breakfast', 'Breakfast'), ('Lunch', 'Lunch'), ('Dinner', 'Dinner')], max_length=15, unique=True)),
                ('price', models.PositiveIntegerField()),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='specialorder',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='specialorder',
            name='user',
        ),
        migrations.RemoveField(
            model_name='transferrequest',
            name='receiver',
        ),
        migrations.RemoveField(
            model_name='transferrequest',
            name='sender',
        ),
        migrations.CreateModel(
            name='BookingRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('status', models.CharField(choices=[('Booked', 'Booked'), ('Canceled', 'Canceled'), ('Consumed', 'Consumed'), ('Missed', 'Missed')], default='Booked', max_length=10)),
                ('booked_at', models.DateTimeField(auto_now_add=True)),
                ('qr_token', models.CharField(default=uuid.uuid4, max_length=50, unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.studentuser')),
                ('meal_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.mealslot')),
            ],
            options={
                'unique_together': {('user', 'meal_type', 'date')},
            },
        ),
        migrations.DeleteModel(
            name='MealBooking',
        ),
        migrations.DeleteModel(
            name='SpecialOrder',
        ),
        migrations.DeleteModel(
            name='TransferRequest',
        ),
    ]
