from conference.models import ConferenceRecord
from django.http import Http404
from django.shortcuts import render


# Create your views here.
def home(request):
    conference_list = ConferenceRecord.objects.filter(active=True).order_by('-id')
    return render(request, "index.html", {'conference_list': conference_list})


def media(request, slug, pk):
    raise Http404
