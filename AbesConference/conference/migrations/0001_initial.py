# Generated by Django 2.1.1 on 2018-09-04 21:37

import conference.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthorRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=55)),
                ('email', models.EmailField(max_length=85)),
                ('mobileNumber', models.CharField(max_length=10)),
                ('country', models.CharField(max_length=55)),
                ('organization', models.CharField(max_length=110)),
                ('webPage', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='ConferenceRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('name', models.CharField(max_length=151)),
                ('description', models.CharField(max_length=1005)),
                ('end_date', models.DateField()),
                ('active', models.BooleanField(default=False)),
                ('submission', models.BooleanField(default=False)),
                ('review', models.BooleanField(default=False)),
                ('status', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PaperRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=210)),
                ('abstract', models.TextField(max_length=1010)),
                ('keywords', models.TextField(max_length=210)),
                ('file', models.FileField(upload_to=conference.models.upload_path)),
                ('status', models.IntegerField(default=3)),
                ('review', models.TextField(default='', max_length=510)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('author', models.ManyToManyField(to='conference.AuthorRecord')),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conference', to='conference.ConferenceRecord')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PcMemberRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pcEmail', models.EmailField(max_length=85)),
                ('name', models.CharField(default='', max_length=80)),
                ('accepted', models.IntegerField(default=0)),
                ('totalPaper', models.IntegerField(default=0)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('demand', models.ManyToManyField(to='conference.PaperRecord')),
                ('pcCon', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pcCon', to='conference.ConferenceRecord')),
            ],
        ),
        migrations.CreateModel(
            name='ReviewPaperRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('overallEvaluation', models.TextField()),
                ('point', models.IntegerField()),
                ('remark', models.CharField(max_length=110)),
                ('accepted', models.IntegerField(default=3)),
                ('complete', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('update', models.DateTimeField(auto_now=True)),
                ('paper', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='paper', to='conference.PaperRecord')),
                ('reviewCon', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviewCon', to='conference.ConferenceRecord')),
                ('reviewUser', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviewUser', to='conference.PcMemberRecord')),
            ],
        ),
    ]
