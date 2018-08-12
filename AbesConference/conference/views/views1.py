# Conference related view

from django.contrib import messages, auth
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from ..forms import ConferenceForm
from ..models import ConferenceRecord


class Conference(TemplateView):
    template_name = 'welcome.html'

    def get(self, request, *args, **kwargs):
        form = ConferenceForm()
        record = ConferenceRecord.objects.all().order_by('-id')
        return render(request, self.template_name, {'form': form, 'record': record})

    def post(self, request, *args, **kwargs):
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

    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_staff:
                instance = ConferenceRecord.objects.get(slug=kwargs['slug'])
                instance.submission = False
                instance.save(update_fields=['submission'])
                msg = "Submission closed of " + kwargs['slug']
                messages.success(request, msg)
                return redirect('conference:welcome')
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('conference:welcome')
        except Exception:
            auth.logout(request)
            return redirect('home')


class StartSubmission(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            instance = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if request.user.is_staff and instance.status:
                instance.submission = True
                instance.save(update_fields=['submission'])
                msg = "Submission open of " + kwargs['slug']
                messages.success(request, msg)
                return redirect('conference:welcome')
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('conference:welcome')
        except Exception:
            auth.logout(request)
            return redirect('home')


class CloseReview(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_staff:
                instance = ConferenceRecord.objects.get(slug=kwargs['slug'])
                instance.review = False
                instance.save(update_fields=['review'])
                msg = "Review closed of " + kwargs['slug']
                messages.success(request, msg)
                return redirect('conference:welcome')
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('conference:welcome')
        except Exception:
            auth.logout(request)
            return redirect('home')


class StartReview(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            instance = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if request.user.is_staff and instance.status:
                instance.review = True
                instance.save(update_fields=['review'])
                msg = "Review open of " + kwargs['slug']
                messages.success(request, msg)
                return redirect('conference:welcome')
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('conference:welcome')
        except Exception:
            auth.logout(request)
            return redirect('home')


class CloseStatus(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_staff:
                instance = ConferenceRecord.objects.get(slug=kwargs['slug'])
                instance.status = False
                instance.review = False
                instance.submission = False
                instance.save(update_fields=['status', 'review', 'submission'])
                msg = kwargs['slug'] + " closed"
                messages.success(request, msg)
                return redirect('conference:welcome')
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('conference:welcome')
        except Exception:
            auth.logout(request)
            return redirect('home')


class StartStatus(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_staff:
                instance = ConferenceRecord.objects.get(slug=kwargs['slug'])
                instance.status = True
                instance.save(update_fields=['status'])
                msg = kwargs['slug'] + " Open"
                messages.success(request, msg)
                return redirect('conference:welcome')
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('conference:welcome')
        except Exception:
            auth.logout(request)
            return redirect('home')
