from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from ..models import PaperRecord, ReviewPaperRecord, ConferenceRecord, PcMemberRecord


class AddPcMember(TemplateView):
    template_name = 'add_pc_member.html'

    def get(self, request, *args, **kwargs):
        try:
            ConferenceRecord.objects.get(slug=kwargs['slug'])
            return render(request, self.template_name, {'slug': kwargs['slug'], 'list1': None, 'list2': None})
        except Exception:
            auth.logout(request)
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            subject = request.POST['subject']
            message = request.POST['message']
            emails = request.POST['emails']
            li =  emails.split('\r\n')
            list1 = []
            list2 = []
            for l in li:
                try:
                    validate_email(l)
                    list1.append(l)
                    try:
                        PcMemberRecord.objects.get(pcCon=con, pcEmail=l)
                    except ObjectDoesNotExist:
                        instance = PcMemberRecord.objects.create(pcCon=con, pcEmail=l)
                        instance.save()
                except:
                    list2.append(l)
            email = EmailMessage(subject, message, to=list1)
            email.send()
            return render(request, self.template_name, {'slug': kwargs['slug'], 'list1': list1, 'list2': list2})
        except Exception:
            auth.logout(request)
            return redirect('home')


class SelectUser(TemplateView):
    template_name = 'user_list.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if request.user.is_staff and con.review:
                paper = PaperRecord.objects.get(conference=con, pk=kwargs['pk'])
                user_list = PcMemberRecord.objects.all()
                list1 = []
                for user in user_list:
                    try:
                        ReviewPaperRecord.objects.get(reviewUser=user, paper=paper)
                        li = [user, True]
                        list1.append(li)
                    except ObjectDoesNotExist:
                        li = [user, False]
                        list1.append(li)
                return render(request, self.template_name, {'slug': kwargs['slug'], 'paper': paper, 'user_list': list1})
            else:
                messages.error(request, 'Review Closed or Invalid User')
                return redirect("conference:slug_welcome", slug=kwargs['slug'])
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted or Invalid Paper')
            return redirect("conference:welcome")
        except Exception:
            auth.logout(request)
            return redirect('home')


class SelectedUser(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if request.user.is_staff and con.review:
                user = PcMemberRecord.objects.get(pk=kwargs['user_pk'])
                paper = PaperRecord.objects.get(conference=con, pk=kwargs['paper_pk'])
                try:
                    ReviewPaperRecord.objects.get(reviewUser=user, paper=paper)
                    messages.error(request, 'Already Assign this user')
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
            return redirect('conference:welcome')
        except Exception:
            auth.logout(request)
            return redirect('home')


class ShowReviews(TemplateView):
    template_name = 'all_reviews.html'

    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_staff:
                con = ConferenceRecord.objects.get(slug=kwargs['slug'])
                paper = PaperRecord.objects.get(conference=con, pk=kwargs['pk'])
                reviews = ReviewPaperRecord.objects.filter(paper=paper)
                return render(request, self.template_name, {'slug': kwargs['slug'], 'paper': paper, 'reviews': reviews})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except Exception:
            auth.logout(request)
            return redirect('home')
