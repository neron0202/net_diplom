# Generated by Django 2.2.13 on 2022-05-31 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orbackend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='productinfo',
            name='model',
            field=models.CharField(blank=True, max_length=100, verbose_name='Модель'),
        ),
    ]
