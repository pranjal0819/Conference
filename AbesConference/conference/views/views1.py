# Conference related view

from django.contrib import messages, auth
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from ..forms import ConferenceForm
from ..models import ConferenceRecord


class CreateConference(TemplateView):
    template_name = 'create_conference.html'

    def get(self, request, *args, **kwargs):
        form = ConferenceForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ConferenceForm(request.POST)
        if form.is_valid():
            temp = form.save(commit=False)
            temp.owner = request.user
            temp.save()
            messages.success(request, 'Successfully Conference Created')
            messages.success(request, 'Check your Email')
            return redirect('home')
        else:
            messages.error(request, 'Contact to admin')
            form = ConferenceForm()
            return render(request, self.template_name, {'form': form})


class CloseSubmission(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            instance = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if request.user == instance.owner:
                instance.submission = False
                instance.save(update_fields=['submission'])
                msg = "Submission closed of " + kwargs['slug']
                messages.success(request, msg)
                return redirect('home')
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('home')
        except Exception:
            auth.logout(request)
            return redirect('home')


class OpenSubmission(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            instance = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if request.user == instance.owner and instance.status:
                instance.submission = True
                instance.save(update_fields=['submission'])
                msg = "Submission open of " + kwargs['slug']
                messages.success(request, msg)
                return redirect('home')
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('home')
        except Exception:
            auth.logout(request)
            return redirect('home')


class CloseReview(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            instance = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if request.user == instance.owner:
                instance.review = False
                instance.save(update_fields=['review'])
                msg = "Review closed of " + kwargs['slug']
                messages.success(request, msg)
                return redirect('home')
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('home')
        except Exception:
            auth.logout(request)
            return redirect('home')


class OpenReview(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            instance = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if request.user == instance.owner and instance.status:
                instance.review = True
                instance.save(update_fields=['review'])
                msg = "Review open of " + kwargs['slug']
                messages.success(request, msg)
                return redirect('home')
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('home')
        except Exception:
            auth.logout(request)
            return redirect('home')


class CloseStatus(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            instance = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if request.user == instance.owner:
                instance.status = False
                instance.review = False
                instance.submission = False
                instance.save(update_fields=['status', 'review', 'submission'])
                msg = kwargs['slug'] + " closed"
                messages.success(request, msg)
                return redirect('home')
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('home')
        except Exception:
            auth.logout(request)
            return redirect('home')


class OpenStatus(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            instance = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if request.user == instance.owner:
                instance.status = True
                instance.save(update_fields=['status'])
                msg = kwargs['slug'] + " Open"
                messages.success(request, msg)
                return redirect('home')
        except ObjectDoesNotExist:
            messages.error(request, 'Contact to admin')
            return redirect('home')
        except Exception:
            auth.logout(request)
            return redirect('home')
