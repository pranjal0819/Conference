# PC Member related Views

from django.contrib import messages, auth
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from .views0 import *


# noinspection PyBroadException
# Error Code X4DA01, X4DA10
class ManagePCMember(TemplateView):
    template = 'view4/manage_pc_member.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X4DA01')
            if owner:
                members = get_all_pc_member(conference)
                return render(request, self.template, {'owner': True, 'slug': kwargs['slug'], 'member_list': members})
            else:
                raise PermissionDenied('Permission Denied. Error Code: X4DA02')
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X4DA10')
            return redirect('home')


# noinspection PyBroadException
# Error Code X4DB01, X4DB02, X4DB03, X4DB10
class ProfilePcMember(TemplateView):
    template_name = 'view4/pc_profile.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X4DB01')
            if owner:
                pc_user = get_pc_member(conference, kwargs['email'], 'X4DB02')
                paper_list = get_all_review_pc_user(conference, pc_user)
                return render(request, self.template_name,
                              {'owner': True, 'slug': kwargs['slug'], 'member': pc_user, 'paper_list': paper_list})
            else:
                raise PermissionDenied('Permission Denied. Error Code: X4DB03')
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X4DB10')
            return redirect('home')


# noinspection PyBroadException
# Error Code X4DC01, X4DC02, X4DC03, X4DC10
class DeletePCMember(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X4DC01')
            if owner:
                pc_user = get_pc_member(conference, kwargs['email'], 'X4DC02')
                pc_user.delete()
                messages.success(request, 'Successfully Deleted')
                return redirect('conference:manage_pc_member', slug=kwargs['slug'])
            else:
                raise PermissionDenied('Permission Denied. Error Code: X4DC03')
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X4DC10')
            return redirect('home')


# noinspection PyBroadException
# Error Code X4DD01, X4DD02, X4DD03, X4DD04, X4DD10
class PcMembersForPaper(TemplateView):
    template = 'view4/pc_members_for_paper.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X4DD01')
            if owner:
                paper = get_paper(conference, kwargs['pk'], 'X4DD02')
                user_list = get_all_accepted_pc_member(conference)
                list1 = []
                for user in user_list:
                    try:
                        instance = get_review_paper(conference, user, paper, 'X4DD03')
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
                raise PermissionDenied('Permission Denied. Error Code: X4DD04')
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X4DD10')
            return redirect('home')


# noinspection PyBroadException
# Error Code X4DE01, X4DE03, X4DE04, X4DE05, X4DE10
class SelectForPaper(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X4DE01')
            if owner:
                user = get_pc_member(conference, kwargs['user_email'], 'X4DE02')
                paper = get_paper(conference, kwargs['paper_pk'], 'X4DE03')
                try:
                    instance = get_review_paper(conference, user, paper, 'X4DE04')
                    instance.delete()
                    user.totalPaper = user.totalPaper - 1
                    user.save(update_fields=['totalPaper'])
                    added = False
                    # messages.success(request, 'Removed Successfully')
                except ObjectDoesNotExist:
                    instance = ReviewPaperRecord.objects.create(reviewUser=user, paper=paper, reviewCon=conference)
                    instance.save()
                    user.totalPaper = user.totalPaper + 1
                    user.save(update_fields=['totalPaper'])
                    added = True
                    # messages.success(request, 'Add Successfully')
                if request.is_ajax():
                    return JsonResponse({'added': added})
                return redirect("conference:select_user", slug=kwargs['slug'], pk=kwargs['paper_pk'])
            else:
                raise PermissionDenied('Permission Denied. Error Code: X4DE05')
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X4DE10')
            return redirect('home')
