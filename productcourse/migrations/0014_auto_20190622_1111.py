# Generated by Django 2.2 on 2019-06-22 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('productcourse', '0013_auto_20190622_1051'),
    ]

    operations = [
        migrations.RenameField(
            model_name='video',
            old_name='name',
            new_name='title',
        ),
    ]
