from django.shortcuts import render
from conference.models import ConferenceRecord

# Create your views here.
def home(request):
    conference_list = ConferenceRecord.objects.all().order_by('-id')
    return render(request, "index.html", {'conference_list':conference_list})


def registration(request):
    return render(request, 'registration.html')


def call_for_paper(request):
    return render(request, 'call-for-paper.html')


def proceeding(request):
    return render(request, 'proceeding.html')
