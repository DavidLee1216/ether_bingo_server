# Generated by Django 3.2.13 on 2022-04-16 09:47

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_alter_bingobids_match_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bingogame',
            name='called_numbers',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), size=None),
        ),
    ]
