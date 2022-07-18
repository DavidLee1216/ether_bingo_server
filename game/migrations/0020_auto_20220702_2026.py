# Generated by Django 3.2.13 on 2022-07-02 12:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game', '0019_auto_20220630_0234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bingogame',
            name='winner',
        ),
        migrations.AddField(
            model_name='bingogame',
            name='winners',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]