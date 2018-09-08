from django.conf import settings
from django.contrib import messages, auth
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.mail import send_mass_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from ..forms import EmailToAuthorsForm
from ..models import PaperRecord, ConferenceRecord


# noinspection PyBroadException
class EmailToAuthors(TemplateView):
    template_name = 'view5/email_to_author.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                paper = PaperRecord.objects.filter(conference=con).order_by('id')
                form = EmailToAuthorsForm()
                return render(request, self.template_name, {'slug': kwargs['slug'], 'owner': True,
                                                            'form': form, 'paper_list': paper})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted or Invalid Paper')
            return redirect('home')
        except PermissionDenied:
            messages.error(request, 'Permission Denied')
            auth.logout(request)
            return redirect('home')
        # except Exception:
        #     messages.error(request, 'Have Some Error')
        #     auth.logout(request)
        #     return redirect('home')

    def post(self, request, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                form = EmailToAuthorsForm(request.POST)
                if form.is_valid():
                    current_site = get_current_site(request)
                    notification = request.POST['notification']
                    review = request.POST['review']
                    sub = request.POST['subject']
                    msg = request.POST['message']
                    num = int(request.POST['total'])
                    email_list = []
                    for i in range(num + 1):
                        try:
                            pk = request.POST['check' + str(i)]
                            paper = PaperRecord.objects.get(pk=pk)
                            message = render_to_string('email_to_author.txt', {
                                'name': paper.user.username,
                                'mess': msg,
                                'chair_name': request.user.first_name + ' ' + request.user.last_name,
                                'chair_email': request.user.email,
                                'conference_name': con.slug,
                                'domain': current_site.domain,
                                'slug': kwargs['slug'],
                            })
                            email = (sub, message, settings.EMAIL_HOST_USER, [paper.user.email])
                            email_list.append(email)
                        except Exception:
                            pass
                        try:
                            t = tuple(email_list)
                            send_mass_mail(t, fail_silently=False)
                        except Exception:
                            messages.error(request, 'Email Sending Failed')
                else:
                    messages.error(request, 'Invalid Inputs')
                paper = PaperRecord.objects.filter(conference=con).order_by('-status')
                form = EmailToAuthorsForm()
                return render(request, self.template_name, {'slug': kwargs['slug'], 'owner': True,
                                                            'form': form, 'paper_list': paper})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted or Invalid Paper')
            return redirect('home')
        except PermissionDenied:
            messages.error(request, 'Permission Denied')
            auth.logout(request)
            return redirect('home')
        # except Exception:
        #     messages.error(request, 'Have Some Error')
        #     auth.logout(request)
        #     return redirect('home')
