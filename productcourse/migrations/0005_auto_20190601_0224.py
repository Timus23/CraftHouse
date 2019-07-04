# Generated by Django 2.2 on 2019-06-01 02:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('productcourse', '0004_enrolled_payment_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoursePayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_name', models.CharField(max_length=255)),
                ('price', models.FloatField()),
                ('course_id', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='productcourse.Course')),
                ('user_id', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='enrolled',
            name='course_id',
        ),
        migrations.RemoveField(
            model_name='enrolled',
            name='price',
        ),
        migrations.AlterField(
            model_name='enrolled',
            name='payment_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='productcourse.CoursePayment'),
        ),
    ]
