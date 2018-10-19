from conference.models import ConferenceRecord
from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.
def home(request):
    conference_list = ConferenceRecord.objects.filter(active=True).order_by('-id')
    return render(request, "index.html", {'conference_list': conference_list})


class MediaBlock(TemplateView):
    def get(self, request, *args, **kwargs):
        raise Http404
