# PC Member related Views

from django.contrib import messages, auth
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from .views0 import *


# noinspection PyBroadException
# Error Code X3DA01, X3DA10
class ManagePCMember(TemplateView):
    template = 'view4/manage_pc_member.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X3DA01')
            if owner:
                members = get_all_pc_member(conference)
                return render(request, self.template, {'owner': True, 'slug': kwargs['slug'], 'member_list': members})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            messages.warning(request, 'Permission Denied. Error Code: X3DA02')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X3DA10')
            return redirect('home')


# noinspection PyBroadException
# Error Code X3DB01, X3DB02, X3DB03, X3DB10
class ProfilePcMember(TemplateView):
    template_name = 'view4/pc_profile.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X3DB01')
            if owner:
                pc_user = get_pc_member(conference, kwargs['email'], 'X3DB02')
                paper_list = get_all_review_paper(conference, pc_user)
                return render(request, self.template_name,
                              {'owner': True, 'slug': kwargs['slug'], 'member': pc_user, 'paper_list': paper_list})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            messages.warning(request, 'Permission Denied. Error Code: X3DB03')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X3DB10')
            return redirect('home')


# noinspection PyBroadException
# Error Code X3DC01, X3DC02, X3DC03, X3DC10
class DeletePCMember(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X3DC01')
            if owner:
                pc_user = get_pc_member(conference, kwargs['email'], 'X3DC02')
                pc_user.delete()
                messages.success(request, 'Successfully Deleted')
                return redirect('conference:manage_pc_member', slug=kwargs['slug'])
            else:
                raise PermissionDenied
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            messages.warning(request, 'Permission Denied. Error Code: X3DC03')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X3DC10')
            return redirect('home')


# noinspection PyBroadException
# Error Code X3DD01, X3DD02, X3DD03, X3DD04, X3DD10
class PcMembersForPaper(TemplateView):
    template = 'view4/pc_members_for_paper.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X3DD01')
            if owner:
                paper = get_paper(conference, kwargs['pk'], 'X3DD02')
                user_list = get_all_accepted_pc_member(conference)
                list1 = []
                for user in user_list:
                    try:
                        instance = get_review_paper(user, paper, 'X3DD03')
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
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            messages.warning(request, 'Permission Denied. Error Code: X3DD04')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X3DD10')
            return redirect('home')


# noinspection PyBroadException
# Error Code X3DE01, X3DE03, X3DE04, X3DE05, X3DE10
class SelectForPaper(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X3DE01')
            if owner:
                user = get_pc_member(conference, kwargs['user_email'], 'X3DE02')
                paper = get_paper(conference, kwargs['paper_pk'], 'X3DE03')
                try:
                    instance = get_review_paper(user, paper, 'X3DE04')
                    instance.delete()
                    added = False
                    # messages.success(request, 'Removed Successfully')
                except ObjectDoesNotExist:
                    instance = ReviewPaperRecord.objects.create(reviewUser=user, paper=paper, reviewCon=conference)
                    instance.save()
                    added = True
                    # messages.success(request, 'Add Successfully')
                if request.is_ajax():
                    return JsonResponse({'added': added})
                return redirect("conference:select_user", slug=kwargs['slug'], pk=kwargs['paper_pk'])
            else:
                raise PermissionDenied
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            messages.warning(request, 'Permission Denied. Error Code: X3DE05')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X3DE10')
            return redirect('home')
