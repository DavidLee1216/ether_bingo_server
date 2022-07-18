# Generated by Django 3.2.13 on 2022-04-17 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0009_alter_bingogame_called_numbers'),
    ]

    operations = [
        migrations.AddField(
            model_name='bingoroomauctionbidhistory',
            name='paid_state',
            field=models.CharField(choices=[(0, 'not'), (1, 'paid'), (2, 'cancelled')], default=0, max_length=10),
        ),
        migrations.AlterField(
            model_name='bingoroomauction',
            name='live',
            field=models.BooleanField(default=False),
        ),
    ]
