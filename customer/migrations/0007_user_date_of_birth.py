# Generated by Django 2.2 on 2019-06-27 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0006_remove_user_date_of_birth'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
    ]
