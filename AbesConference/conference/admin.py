from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(PaperRecord)
admin.site.register(AuthorRecord)
admin.site.register(ReviewPaperRecord)
admin.site.register(ConferenceRecord)
admin.site.register(PcMemberRecord)
