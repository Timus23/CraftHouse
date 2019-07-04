# Generated by Django 2.2 on 2019-06-18 07:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('productcourse', '0009_auto_20190613_0746'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categories',
            name='parent_cat_id',
        ),
        migrations.AlterField(
            model_name='questions',
            name='correct_answer',
            field=models.CharField(choices=[('1', 'option1'), ('2', 'option2'), ('3', 'option3'), ('4', 'option4')], default='1', max_length=2),
        ),
        migrations.AlterField(
            model_name='questions',
            name='test_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question', to='productcourse.Test'),
        ),
    ]