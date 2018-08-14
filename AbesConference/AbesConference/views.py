from django.shortcuts import render


# Create your views here.
def home(request):
    return render(request, "index.html", {})


def registration(request):
    return render(request, 'registration.html')


def call_for_paper(request):
    return render(request, 'call-for-paper.html')


def proceeding(request):
    return render(request, 'proceeding.html')
