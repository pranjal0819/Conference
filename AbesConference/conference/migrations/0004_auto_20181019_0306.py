# Generated by Django 2.1.1 on 2018-10-18 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conference', '0003_auto_20181019_0250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paperrecord',
            name='remark',
            field=models.TextField(default='', max_length=510),
        ),
        migrations.AlterField(
            model_name='reviewpaperrecord',
            name='overallEvaluation',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='reviewpaperrecord',
            name='remark',
            field=models.CharField(default='', max_length=510),
        ),
    ]