# Generated by Django 4.0.3 on 2022-03-22 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='first_name',
            field=models.CharField(default='', max_length=30, verbose_name='first name'),
        ),
        migrations.AddField(
            model_name='user',
            name='last_name',
            field=models.CharField(default='', max_length=30, verbose_name='last name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=30, unique=True, verbose_name='user name'),
        ),
    ]
