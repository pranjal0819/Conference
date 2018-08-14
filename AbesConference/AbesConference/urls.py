from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('registration/', registration, name='registration'),
    path('call-for-paper/', call_for_paper, name='callForPaper'),
    path('proceeding/', proceeding, name='proceeding'),

    path('account/', include(('account.urls', 'account'), namespace='account')),

    path('conference/', include(('conference.urls', 'conference'), namespace='conference')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
