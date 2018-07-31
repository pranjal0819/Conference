from django.contrib.auth.models import User
from django.db import models
from datetime import date


# Create your models here.
class AuthorRecord(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    mobileNumber = models.CharField(max_length=10)
    country = models.CharField(max_length=50)
    organization = models.CharField(max_length=100)
    webpage = models.URLField()

    def __str__(self):
        return str(self.name)


class PaperRecord(models.Model):
    title = models.CharField(max_length=100)
    abstract = models.TextField(max_length=500)
    keywords = models.TextField(max_length=100)
    file = models.FileField()
    status = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    author = models.ManyToManyField(AuthorRecord)

    def __str__(self):
        return str(self.title)


class ReviewPaperRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, related_name='user')
    paper = models.ForeignKey(PaperRecord, on_delete=models.PROTECT, null=True, related_name='paper')
    overallEvaluation = models.TextField()
    point = models.IntegerField()
    remark = models.CharField(max_length=100)

    def __str__(self):
        return str(self.user) + " -- " + str(self.paper)
