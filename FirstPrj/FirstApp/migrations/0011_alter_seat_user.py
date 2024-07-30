# Generated by Django 5.0.7 on 2024-07-30 01:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FirstApp', '0010_alter_movie_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seat',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='FirstApp.user'),
        ),
    ]
