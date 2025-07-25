# Generated by Django 5.0.14 on 2025-07-06 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StudentUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('rollnumber', models.CharField(max_length=20)),
                ('department', models.CharField(max_length=50)),
                ('gender', models.CharField(max_length=10)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=200)),
                ('refund_wallet', models.DecimalField(decimal_places=2, default=15000.0, max_digits=10)),
            ],
        ),
    ]
