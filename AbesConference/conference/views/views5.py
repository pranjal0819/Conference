from django.conf import settings
from django.contrib import messages, auth
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.core.mail import send_mail, BadHeaderError, send_mass_mail
from django.core.validators import validate_email
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import TemplateView

from ..forms import EmailForm, AddPcMemberForm
from ..models import PaperRecord, ReviewPaperRecord, ConferenceRecord, PcMemberRecord


# noinspection PyBroadException
class EmailToAuthor(TemplateView):
    template_name = 'view5/email_to_author.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                paper = PaperRecord.objects.filter(conference=con).order_by('id')
                return render(request, self.template_name, {'slug': kwargs['slug'], 'owner': True, 'paper_list': paper})
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
                num = int(request.POST['total'])
                for i in range(num + 1):
                    try:
                        pk = request.POST['check' + str(i)]
                        paper = PaperRecord.objects.get(pk=pk)
                        print(paper)
                    except Exception:
                        pass
                paper = PaperRecord.objects.filter(conference=con).order_by('id')
                return render(request, self.template_name, {'slug': kwargs['slug'], 'owner': True, 'paper_list': paper})
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
