from django.contrib import admin
from .models import PaperRecord, AuthorRecord, ReviewPaperRecord

# Register your models here.
admin.site.register(PaperRecord)
admin.site.register(AuthorRecord)
admin.site.register(ReviewPaperRecord)
