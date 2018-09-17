# PC Member related Views

from django.contrib import messages, auth
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from ..models import PaperRecord, ReviewPaperRecord, ConferenceRecord, PcMemberRecord


# noinspection PyBroadException
class ManagePCMember(TemplateView):
    template = 'view4/manage_pc_member.html'

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
        # except Exception:
        #     messages.error(request, 'Have Some Error')
        #     auth.logout(request)
        #     return redirect('home')


class ProfilePcMember(TemplateView):
    template_name = 'view4/pc_profile.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                member = PcMemberRecord.objects.get(pcCon=con, pcEmail=kwargs['email'])
                paper_list = ReviewPaperRecord.objects.filter(reviewCon=con, reviewUser=member)
                return render(request, self.template_name,
                              {'owner': True, 'slug': kwargs['slug'], 'member': member, 'paper_list': paper_list})
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
class DeletePCMember(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                member = PcMemberRecord.objects.get(pcCon=con, pcEmail=kwargs['email'])
                member.delete()
                messages.success(request, 'successfully Deleted')
                return redirect('conference:manage_pc_member', slug=kwargs['slug'])
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
class PcMembersForPaper(TemplateView):
    template = 'view4/pc_members_paper.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                paper = PaperRecord.objects.get(conference=con, pk=kwargs['pk'])
                user_list = PcMemberRecord.objects.filter(pcCon=con, accepted=5)
                list1 = []
                for user in user_list:
                    try:
                        instance = ReviewPaperRecord.objects.get(reviewUser=user, paper=paper)
                        li = [user, False, True, False]
                        if instance.complete:
                            li[3] = True
                    except ObjectDoesNotExist:
                        li = [user, False, False, False]
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


# noinspection PyBroadException
class SelectForPaper(TemplateView):

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
