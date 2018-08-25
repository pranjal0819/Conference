# PC Member related Views

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
from ..tokens import account_activation_token


class PcMemberList(TemplateView):
    template = 'pc_member_list.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                member_list = PcMemberRecord.objects.all()
                return render(request, self.template,
                              {'owner': True, 'slug': kwargs['slug'], 'member_list': member_list})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted or Invalid Paper')
            return redirect('home')
        except PermissionDenied:
            messages.error(request, 'Permission Denied')
            auth.logout(request)
            return redirect('home')
        except Exception:
            messages.error(request, 'Have Some Error')
            auth.logout(request)
            return redirect('home')


class AddPcMember(TemplateView):
    template_name = 'add_pc_member.html'

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
                form = AddPcMemberForm(request.POST)
                list1 = []
                list2 = []
                if form.is_valid():
                    li = request.POST['emails'].split('\r\n')
                    mess = request.POST['message']
                    email_list = []
                    for l in li:
                        info = l.split(',')
                        try:
                            validate_email(info[2])
                            name = info[0] + ' ' + info[1]
                            try:
                                user = PcMemberRecord.objects.get(pcCon=con, pcEmail=info[2])
                            except ObjectDoesNotExist:
                                user = PcMemberRecord.objects.create(pcCon=con, pcEmail=info[2], name=name)
                            if user.accepted == 5:
                                raise ValidationError('Already Exit')
                            list1.append(info[2])
                            current_site = get_current_site(request)
                            mail_subject = 'Invitation to ' + con.slug + ' program committee'
                            message = render_to_string('pc_confirm_mail.html', {
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
                            email = (mail_subject, message, settings.EMAIL_HOST_USER, [user.pcEmail])
                            email_list.append(email)
                        except IndexError:
                            pass
                        except ValidationError:
                            list2.append(info[2])
                    t = tuple(email_list)
                    send_mass_mail(t, fail_silently=False)
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


class PcMembers(TemplateView):
    template = 'pc_members.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                paper = PaperRecord.objects.get(conference=con, pk=kwargs['pk'])
                user_list = PcMemberRecord.objects.filter(pcCon=con, accepted=5)
                list1 = []
                for user in user_list:
                    try:
                        ReviewPaperRecord.objects.get(reviewUser=user, paper=paper)
                        li = [user, False, True]
                    except ObjectDoesNotExist:
                        li = [user, False, False]
                    if paper in user.demand.all():
                        li[1] = True
                    list1.append(li)
                return render(request, self.template,
                              {'owner': True, 'slug': kwargs['slug'], 'paper': paper, 'user_list': list1})
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
        #     auth.logout(request)
        #     return redirect('home')


class SelectedUser(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                user = PcMemberRecord.objects.get(pk=kwargs['user_pk'])
                paper = PaperRecord.objects.get(conference=con, pk=kwargs['paper_pk'])
                try:
                    instance = ReviewPaperRecord.objects.get(reviewUser=user, paper=paper)
                    instance.delete()
                    messages.success(request, 'Removed successfully')
                except ObjectDoesNotExist:
                    instance = ReviewPaperRecord.objects.create(reviewUser=user, paper=paper, reviewCon=con,
                                                                overallEvaluation='', remark='', point=0)
                    instance.save()
                    messages.success(request, 'Successfully record save')
                return redirect("conference:select_user", slug=kwargs['slug'], pk=kwargs['paper_pk'])
            else:
                messages.error(request, 'Review Closed or Invalid User')
                return redirect("conference:slug_welcome", slug=kwargs['slug'])
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')


# class DeselectUser(TemplateView):
#
#     def get(self, request, *args, **kwargs):
#         try:
#             con = ConferenceRecord.objects.get(slug=kwargs['slug'])
#             if con.owner == request.user or request.user.is_staff:
#                 user = PcMemberRecord.objects.get(pk=kwargs['user_pk'])
#                 paper = PaperRecord.objects.get(conference=con, pk=kwargs['paper_pk'])
#                 try:
#                     instance = ReviewPaperRecord.objects.get(reviewUser=user, paper=paper)
#                     instance.delete()
#                     messages.success(request, 'Updated')
#                 except ObjectDoesNotExist:
#                     messages.error(request, 'Invalid request')
#                 return redirect("conference:select_user", slug=kwargs['slug'], pk=kwargs['paper_pk'])
#             else:
#                 messages.error(request, 'Review Closed or Invalid User')
#                 return redirect("conference:slug_welcome", slug=kwargs['slug'])
#         except ObjectDoesNotExist:
#             messages.error(request, 'Conference Closed or Deleted')
#             return redirect('home')
#             # except Exception:
#             # auth.logout(request)
#             # return redirect('home')


class ShowReviews(TemplateView):
    template_name = 'all_reviews.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                paper = PaperRecord.objects.get(conference=con, pk=kwargs['pk'])
                reviews = ReviewPaperRecord.objects.filter(paper=paper)
                return render(request, self.template_name,
                              {'owner': True, 'slug': kwargs['slug'], 'paper': paper, 'reviews': reviews})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')

    def post(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                paper = PaperRecord.objects.get(conference=con, pk=kwargs['pk'])
                paper.status = int(request.POST['point'])
                paper.review = request.POST['review']
                paper.save(update_fields=['status', 'review'])
                messages.success(request, 'Successfully update remarks')
                return redirect('conference:view_detail', slug=kwargs['slug'], pk=kwargs['pk'])
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')
