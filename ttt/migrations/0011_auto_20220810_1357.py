# Generated by Django 3.2.5 on 2022-08-10 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ttt', '0010_auto_20220809_2240'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='ptype',
        ),
        migrations.AlterField(
            model_name='player',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
