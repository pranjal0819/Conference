# Generated by Django 2.1a1 on 2018-08-23 21:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('conference', '0007_auto_20180824_0208'),
    ]

    operations = [
        migrations.AddField(
            model_name='pcmemberrecord',
            name='demand',
            field=models.ManyToManyField(to='conference.PaperRecord'),
        ),
    ]
