# Generated by Django 2.1a1 on 2018-08-08 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conference', '0004_auto_20180809_0148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paperrecord',
            name='abstract',
            field=models.TextField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='paperrecord',
            name='keywords',
            field=models.TextField(max_length=200),
        ),
        migrations.AlterField(
            model_name='paperrecord',
            name='title',
            field=models.CharField(max_length=200),
        ),
    ]