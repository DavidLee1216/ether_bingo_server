# Generated by Django 3.2.13 on 2022-05-21 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0014_alter_bingoroomauctionbidhistory_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='bingoroom',
            name='owner_room_history_id',
            field=models.IntegerField(default=0),
        ),
    ]
