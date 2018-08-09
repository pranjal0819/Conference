from django.contrib import messages, auth
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from ..forms import ConferenceForm
from ..models import ConferenceRecord


class Conference(TemplateView):
    template_name = 'welcome.html'

    def get(self, request):
        form = ConferenceForm()
        record = ConferenceRecord.objects.all().order_by('-id')
        return render(request, self.template_name, {'form': form, 'record': record})

    def post(self, request):
        form = ConferenceForm(request.POST)
        if form.is_valid() and request.user.is_staff:
            form.save()
            messages.success(request, 'Successfully Conference Created')
        else:
            messages.error(request, 'Contact to admin')
        form = ConferenceForm()
        record = ConferenceRecord.objects.all().order_by('-id')
        return render(request, self.template_name, {'form': form, 'record': record})


class CloseSubmission(TemplateView):

    def get(self, request, slug):
        try:
            if request.user.is_staff:
                instance = ConferenceRecord.objects.get(slug=slug)
                instance.submission = False
                instance.save(update_fields=['submission'])
                msg = "Submission closed of " + slug
                messages.success(request, msg)
                return redirect('conference:welcome')
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class StartSubmission(TemplateView):

    def get(self, request, slug):
        try:
            instance = ConferenceRecord.objects.get(slug=slug)
            if request.user.is_staff and instance.status:
                instance.submission = True
                instance.save(update_fields=['submission'])
                msg = "Submission open of " + slug
                messages.success(request, msg)
                return redirect('conference:welcome')
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class CloseReview(TemplateView):

    def get(self, request, slug):
        try:
            if request.user.is_staff:
                instance = ConferenceRecord.objects.get(slug=slug)
                instance.review = False
                instance.save(update_fields=['review'])
                msg = "Review closed of " + slug
                messages.success(request, msg)
                return redirect('conference:welcome')
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class StartReview(TemplateView):

    def get(self, request, slug):
        try:
            instance = ConferenceRecord.objects.get(slug=slug)
            if request.user.is_staff and instance.status:
                instance.review = True
                instance.save(update_fields=['review'])
                msg = "Review open of " + slug
                messages.success(request, msg)
                return redirect('conference:welcome')
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class CloseStatus(TemplateView):

    def get(self, request, slug):
        try:
            if request.user.is_staff:
                instance = ConferenceRecord.objects.get(slug=slug)
                instance.status = False
                instance.review = False
                instance.submission = False
                instance.save(update_fields=['status', 'review', 'submission'])
                msg = slug + " closed"
                messages.success(request, msg)
                return redirect('conference:welcome')
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class StartStatus(TemplateView):

    def get(self, request, slug):
        try:
            if request.user.is_staff:
                instance = ConferenceRecord.objects.get(slug=slug)
                instance.status = True
                instance.save(update_fields=['status'])
                msg = slug + " Open"
                messages.success(request, msg)
                return redirect('conference:welcome')
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')
