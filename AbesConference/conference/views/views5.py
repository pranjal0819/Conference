# Email related Views

from django.conf import settings
from django.contrib import messages, auth
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.core.mail import send_mail, BadHeaderError, EmailMessage, send_mass_mail
from django.core.validators import validate_email
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import TemplateView

from ..forms import EmailForm, AddPcMemberForm, EmailToAuthorsForm
from ..models import PaperRecord, ReviewPaperRecord, ConferenceRecord, PcMemberRecord
from ..tokens import account_activation_token


# noinspection PyBroadException
class EmailToAuthors(TemplateView):
    template_name = 'view5/email_to_author.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                paper = PaperRecord.objects.filter(conference=con).order_by('id')
                form = EmailToAuthorsForm()
                attr = {'slug': kwargs['slug'], 'owner': True, 'form': form, 'paper_list': paper}
                return render(request, self.template_name, attr)
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
                    review = None
                    email_list = []
                    review_list = None
                    current_site = get_current_site(request)
                    # notification = request.POST['notification']
                    try:
                        review = form.cleaned_data['review']
                    except Exception:
                        pass
                    sub = form.cleaned_data['subject']
                    msg = form.cleaned_data['message']
                    num = int(request.POST['total'])
                    for i in range(1, num + 1, 1):
                        try:
                            pk = request.POST['check' + str(i)]
                            paper = PaperRecord.objects.get(conference=con, pk=pk)
                            if review:
                                review_list = ReviewPaperRecord.objects.filter(paper=paper, complete=True)
                            message = render_to_string('email_to_author.txt', {
                                'name': paper.user.username,
                                'mess': msg,
                                'review_list': review_list,
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
                        messages.success(request, 'Email Send Successfully')
                    except Exception:
                        messages.error(request, 'Email Sending Failed')
                else:
                    messages.error(request, 'Invalid Inputs')
                paper = PaperRecord.objects.filter(conference=con).order_by('-status')
                form = EmailToAuthorsForm()
                attr = {'slug': kwargs['slug'], 'owner': True, 'form': form, 'paper_list': paper}
                return render(request, self.template_name, attr)
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


# noinspection PyBroadException
class AddPcMember(TemplateView):
    template_name = 'view5/add_pc_member.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                form = AddPcMemberForm()
                attr = {'owner': True,
                        'slug': kwargs['slug'],
                        'list1': None,
                        'list2': None,
                        'form': form}
                return render(request, self.template_name, attr)
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
        except PermissionDenied:
            messages.error(request, 'Permission Denied')
            auth.logout(request)
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')

    def post(self, request, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                form = AddPcMemberForm(request.POST, request.FILES)
                list1 = []
                list2 = []
                file = None
                if form.is_valid():
                    li = form.cleaned_data['emails'].split('\r\n')
                    mess = form.cleaned_data['message']
                    try:
                        file = form.cleaned_data['file']
                        content = file.read()
                    except Exception:
                        content = None
                        pass
                    current_site = get_current_site(request)
                    mail_subject = 'Invitation to ' + con.slug + ' program committee'
                    for l in li:
                        info = l.split(',')
                        try:
                            validate_email(info[2])
                            name = info[0] + ' ' + info[1]
                            try:
                                user = PcMemberRecord.objects.get(pcCon=con, pcEmail=info[2])
                                if user.accepted == 5:
                                    raise ValidationError('Email Invalid')
                            except ObjectDoesNotExist:
                                user = PcMemberRecord.objects.create(pcCon=con, pcEmail=info[2], name=name)
                            list1.append(info[2])
                            message = render_to_string('pc_confirm_mail.txt', {
                                'sender_name': name,
                                'mess': mess,
                                'chair_name': request.user.first_name + ' ' + request.user.last_name,
                                'chair_email': request.user.email,
                                'conference_name': con.slug,
                                'domain': current_site.domain,
                                'slug': kwargs['slug'],
                                'uid': urlsafe_base64_encode(force_bytes(user.pcEmail)).decode(),
                                'token': account_activation_token.make_token(user),
                            })
                            email = EmailMessage(mail_subject, message, to=[user.pcEmail])
                            if file and content:
                                email.attach(file.name, content, 'application/pdf')
                            email.send()
                        except IndexError:
                            pass
                        except ValidationError:
                            list2.append(info[2])
                        except Exception:
                            messages.error(request, 'Mail Sending Fail')
                else:
                    messages.error(request, 'Try Again')
                form = AddPcMemberForm()
                attr = {'owner': True,
                        'slug': kwargs['slug'],
                        'list1': list1,
                        'list2': list2,
                        'form': form}
                return render(request, self.template_name, attr)
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
        except PermissionDenied:
            messages.error(request, 'Permission Denied')
            auth.logout(request)
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')


# noinspection PyBroadException
def confirm(request, slug, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        con = ConferenceRecord.objects.get(slug=slug)
        user = PcMemberRecord.objects.get(pcCon=con, pcEmail=uid)
    except Exception:
        user = None
        con = None
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            if request.POST['accept'] == "True":
                user.accepted = 5
                messages.success(request, 'Thank You for Accepting')
            else:
                user.accepted = 3
                messages.error(request, 'You rejected')
            user.save()
            return redirect("home")
        else:
            return render(request, "confirmation.html", {'conference': con})
    else:
        messages.error(request, 'Activation link is invalid! Contact to Us')
        return redirect("home")


# noinspection PyBroadException
class SendEmail(TemplateView):
    template = 'send_email.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                pc = PcMemberRecord.objects.get(pcCon=con, pk=kwargs['pk'])
                form = EmailForm()
                return render(request, self.template, {'owner': True, 'con': con, 'pc_user': pc, 'form': form})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
        except PermissionDenied:
            messages.error(request, 'Permission Denied')
            auth.logout(request)
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')

    def post(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                pc = PcMemberRecord.objects.get(pcCon=con, pk=kwargs['pk'])
                form = EmailForm(request.POST)
                if form.is_valid():
                    subject = form.cleaned_data['subject']
                    message = form.cleaned_data['message']
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [pc.pcEmail])
                    messages.success(request, 'Successfully send email to' + pc.pcEmail)
                else:
                    messages.error(request, 'Invalid Form')
                form = EmailForm()
                return render(request, self.template, {'owner': True, 'con': con, 'pc_user': pc, 'form': form})
            else:
                raise PermissionDenied
        except BadHeaderError:
            return redirect('home')
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
        except PermissionDenied:
            messages.error(request, 'Permission Denied')
            auth.logout(request)
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')
