# Email related Views

from django.conf import settings
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, BadHeaderError, EmailMessage, send_mass_mail
from django.core.validators import validate_email
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import TemplateView

from .views0 import *
from ..forms import *
from ..tokens import account_activation_token


# noinspection PyBroadException
# Error Code X5EA01, X5EA02, X5EA10, X5EA11, X5EA12, X5EA13, X5EA20
class AddPcMember(TemplateView):
    template_name = 'view5/add_pc_member.html'
    max_email = 10

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X5EA01')
            if owner:
                form = AddPcMemberForm()
                attr = {'owner': True, 'slug': kwargs['slug'], 'list1': None, 'list2': None, 'form': form}
                return render(request, self.template_name, attr)
            else:
                raise PermissionDenied('Permission Denied. Error Code: X5EA02')
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X5EA10')
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X5EA11')
            if owner:
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
                    mail_subject = 'Invitation to ' + conference.slug + ' program committee'
                    i = 0
                    for l in li:
                        info = l.split(',')
                        try:
                            i = i + 1
                            if i >= self.max_email:
                                raise ValidationError("Only 10 emails at a time")
                            info[2] = info[2].lower()
                            validate_email(info[2])
                            name = info[0] + ' ' + info[1]
                            try:
                                user = PcMemberRecord.objects.get(pcCon=conference, pcEmail=info[2])
                                if user.accepted == 5:
                                    raise ValidationError('Email Invalid')
                            except ObjectDoesNotExist:
                                user = PcMemberRecord.objects.create(pcCon=conference, pcEmail=info[2], name=name)
                            list1.append(info[2])
                            message = render_to_string('pc_confirm_mail.txt', {
                                'sender_name': name,
                                'mess': mess,
                                'chair_name': request.user.first_name + ' ' + request.user.last_name,
                                'chair_email': request.user.email,
                                'conference_name': conference.slug,
                                'domain': current_site.domain,
                                'slug': kwargs['slug'],
                                'uid': urlsafe_base64_encode(force_bytes(user.pcEmail)).decode(),
                                'token': account_activation_token.make_token(user),
                            })
                            email = EmailMessage(mail_subject, message, to=[user.pcEmail])
                            if file and content:
                                i = i + 1
                                email.attach(file.name, content, 'application/pdf')
                            email.send()
                        except IndexError:
                            pass
                        except ValidationError:
                            list2.append(info[2])
                        except Exception:
                            messages.error(request, 'Mail Sending Fail. Error Code: X5EA12')
                else:
                    messages.error(request, 'Try Again')
                form = AddPcMemberForm()
                attr = {'owner': True, 'slug': kwargs['slug'], 'list1': list1, 'list2': list2, 'form': form}
                return render(request, self.template_name, attr)
            else:
                raise PermissionDenied('Permission Denied. Error Code: X5EA13')
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X5EA20')
            return redirect('home')


# noinspection PyBroadException
# Error Code X5EB01, X5EB02, X5EB03, X5EB10, X5EB11, X5EB12, X5EB13, X5EB20
class PcConfirmation(TemplateView):
    template_name = 'view5/confirmation.html'

    def get(self, request, *args, **kwargs):
        try:
            email = force_text(urlsafe_base64_decode(kwargs['uidb64']))
            try:
                u = User.objects.get(email=email)
            except ObjectDoesNotExist:
                u = None
            if u is None or not u.is_active:
                messages.info(request, 'Must have an Account')
                return redirect('account:signup')
            conference, owner = get_conference(request, kwargs['slug'], 'X5EB01')
            user = get_pc_member(conference, email, 'X5EB02')
            if account_activation_token.check_token(user, kwargs['token']):
                form = PcConfirmationForm()
                return render(request, self.template_name, {'conference': conference, 'form': form})
            else:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            messages.info(request, 'Activation link is invalid! Contact to Us. X5EB03')
            return redirect('home')
        except Exception:
            messages.error(request, 'Error Code: X5EB10')
            return redirect('home')

    @staticmethod
    def post(request, **kwargs):
        try:
            email = force_text(urlsafe_base64_decode(kwargs['uidb64']))
            conference, owner = get_conference(request, kwargs['slug'], 'X5EB11')
            user = get_pc_member(conference, email, 'X5EB12')
            if account_activation_token.check_token(user, kwargs['token']):
                form = PcConfirmationForm(request.POST)
                if form.is_valid():
                    user.accepted = form.cleaned_data['accept']
                    user.save(update_fields=['accepted'])
                    if user.accepted == 5:
                        messages.success(request, 'Thank You for Accepting Invitation')
                    else:
                        messages.warning(request, 'You rejected Pc Member Invitation')
                else:
                    messages.error(request, 'Invalid Response')
                return redirect("home")
            else:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            messages.info(request, 'Activation link is invalid! Contact to Us. X5EB13')
            return redirect('home')
        except Exception:
            messages.error(request, 'Error Code: X5EB20')
            return redirect('home')


# noinspection PyBroadException
# Error Code X5EC01, X5EC02, X5EC10, X5EC11, X5EC12, X5EC20
class EmailToAuthors(TemplateView):
    template_name = 'view5/email_to_author.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X5EC01')
            if owner:
                paper = get_all_paper(conference)
                form = EmailToAuthorsForm()
                attr = {'slug': kwargs['slug'], 'owner': owner, 'form': form, 'paper_list': paper}
                return render(request, self.template_name, attr)
            else:
                raise PermissionDenied('Permission Denied. Error Code: X5EC02')
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X5EC10')
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X5EC11')
            if owner:
                form = EmailToAuthorsForm(request.POST)
                if form.is_valid():
                    email_list = []
                    review_list = None
                    current_site = get_current_site(request)
                    # notification = request.POST['notification']
                    try:
                        review = form.cleaned_data['review']
                    except Exception:
                        review = None
                    sub = form.cleaned_data['subject']
                    msg = form.cleaned_data['message']
                    num = int(request.POST['total'])
                    for i in range(1, num + 1, 1):
                        try:
                            pk = request.POST['check' + str(i)]
                            paper = get_paper(conference, pk, '')
                            if review:
                                review_list = get_all_review_paper_complete(conference, paper, True)
                            message = render_to_string('email_to_author.txt', {
                                'name': paper.user.username,
                                'mess': msg,
                                'review_list': review_list,
                                'chair_name': request.user.first_name + ' ' + request.user.last_name,
                                'chair_email': request.user.email,
                                'conference_name': conference.name,
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
                paper = get_all_paper(conference)
                form = EmailToAuthorsForm()
                attr = {'slug': kwargs['slug'], 'owner': owner, 'form': form, 'paper_list': paper}
                return render(request, self.template_name, attr)
            else:
                raise PermissionDenied('Permission Denied. Error Code: X5EC12')
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X5EC20')
            return redirect('home')


# noinspection PyBroadException
# Error Code X5ED01, X5ED02, X5ED03, X5ED10, X5ED11, X5ED12, X5ED13, X5ED20
class SendEmail(TemplateView):
    template = 'send_email.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X5ED11')
            if owner:
                pc = PcMemberRecord.objects.get(pcCon=conference, pk=kwargs['pk'])
                form = EmailForm()
                return render(request, self.template,
                              {'slug': kwargs['slug'], 'owner': owner, 'pc_user': pc, 'form': form})
            else:
                raise PermissionDenied('Permission Denied. Error Code: X5EAD03')
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X5ED10')
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X5ED11')
            if owner:
                pc = PcMemberRecord.objects.get(pcCon=conference, pk=kwargs['pk'])
                form = EmailForm(request.POST)
                if form.is_valid():
                    subject = form.cleaned_data['subject']
                    message = form.cleaned_data['message']
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [pc.pcEmail])
                    messages.success(request, 'Successfully send email to' + pc.pcEmail)
                else:
                    messages.error(request, 'Invalid Form')
                form = EmailForm()
                return render(request, self.template,
                              {'slug': kwargs['slug'], 'owner': owner, 'pc_user': pc, 'form': form})
            else:
                raise PermissionDenied('Permission Denied. Error Code: X5ED13')
        except BadHeaderError:
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X5ED20')
            return redirect('home')
