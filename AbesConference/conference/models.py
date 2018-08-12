import random

from django.contrib.auth.models import User
from django.db import models

from .utils import unique_slug_generator


# Create your models here.
def upload_path(instance, filename):
    file_base, ext = filename.split(".")
    new_filename = str(random.randint(10000, 953205))
    final_filename = '{new_filename}.{ext}'.format(new_filename=new_filename, ext=ext)
    return "{folder}/{final_filename}".format(folder=instance.conference, final_filename=final_filename)


class ConferenceRecord(models.Model):
    slug = models.SlugField(unique=True, blank=True)
    description = models.CharField(max_length=500)
    start_date = models.DateField()
    end_date = models.DateField()
    submission = models.BooleanField(default=True)
    review = models.BooleanField(default=True)
    status = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.slug


def conference_pre_save(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


models.signals.pre_save.connect(conference_pre_save, sender=ConferenceRecord)


class AuthorRecord(models.Model):
    name = models.CharField(max_length=55)
    email = models.CharField(max_length=55)
    mobileNumber = models.CharField(max_length=10)
    country = models.CharField(max_length=55)
    organization = models.CharField(max_length=110)
    webPage = models.URLField()

    def __str__(self):
        return self.name


class PaperRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    conference = models.ForeignKey(ConferenceRecord, on_delete=models.CASCADE, related_name='conference')
    title = models.CharField(max_length=210)
    abstract = models.TextField(max_length=1010)
    keywords = models.TextField(max_length=210)
    file = models.FileField(upload_to=upload_path)
    status = models.IntegerField(default=3)
    # review = models.TextField(max_length=510)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    author = models.ManyToManyField(AuthorRecord)

    def __str__(self):
        return str(self.title)


class ReviewPaperRecord(models.Model):
    reviewUser = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='reviewUser')
    paper = models.ForeignKey(PaperRecord, on_delete=models.CASCADE, null=True, related_name='paper')
    reviewCon = models.ForeignKey(ConferenceRecord, on_delete=models.CASCADE, null=True, related_name='reviewCon')
    overallEvaluation = models.TextField()
    point = models.IntegerField()
    remark = models.CharField(max_length=110)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.reviewUser) + " -- " + str(self.paper)
