# Generated by Django 2.2 on 2019-06-22 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productcourse', '0012_enrolled_course_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='video_url',
            field=models.CharField(max_length=255),
        ),
    ]
