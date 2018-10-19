from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),

    path('account/', include(('account.urls', 'account'), namespace='account')),

    path('conference/', include(('conference.urls', 'conference'), namespace='conference')),
    path('media/<slug>/<pk>', MediaBlock.as_view()),
    path('media/<slug>', MediaBlock.as_view()),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
