# Generated by Django 3.1.4 on 2024-07-29 02:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FirstApp', '0005_auto_20240729_0234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seat',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='FirstApp.user'),
        ),
    ]