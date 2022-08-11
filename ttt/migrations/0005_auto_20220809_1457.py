# Generated by Django 3.2.5 on 2022-08-09 09:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ttt', '0004_alter_game_uid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cell',
            name='marked_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cells', to='ttt.player'),
        ),
        migrations.AlterField(
            model_name='cell',
            name='status',
            field=models.CharField(choices=[('BLANK', 'blank'), ('MARKED', 'marked')], default='blank', max_length=20),
        ),
    ]