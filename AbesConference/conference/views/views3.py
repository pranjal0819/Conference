# Reviewer related view

from django.contrib import messages, auth
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from .views0 import *
from ..forms import ReviewPaperForm, ReviewConfirmationForm


# noinspection PyBroadException
# Error X3CA01, X3CA02, X3CA10
class AcceptToReview(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X3CA01')
            pc_member = get_pc_member(conference, request.user.email, 'X3CA02')
            pc_member.accepted = 5
            pc_member.save(update_fields=['accepted'])
            return redirect('conference:review_list', slug=kwargs['slug'])
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X3CA10')
            return redirect('home')


# noinspection PyBroadException
# Error X3CB01, X3CB02, X3CB10
class ReviewPaperList(TemplateView):
    template = 'view3/review_paper_list.html'

    def get(self, request, *args, **kwargs):
        try:
            list1 = []
            list2 = []
            list3 = []
            accept = False
            conference, owner = get_conference(request, kwargs['slug'], 'X3CB01')
            pc_member = get_pc_member(conference, request.user.email, 'X3CB02')
            if pc_member.accepted == 5:
                accept = True
                paper_list = get_all_paper(conference)
                for paper in paper_list:
                    try:
                        obj = get_review_paper(conference, pc_member, paper, '')
                        if obj.complete:
                            list2.append(obj)
                        else:
                            list1.append(obj)
                    except ObjectDoesNotExist:
                        list3.append(paper)
            else:
                messages.warning(request, 'Please Accept to Review')
            attr = {'owner': owner, 'slug': kwargs['slug'], 'pc_member': pc_member, 'accept': accept, 'list1': list1,
                    'list2': list2, 'list3': list3}
            return render(request, self.template, attr)
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X3CB10')
            return redirect('home')


# noinspection PyBroadException
# Error X3CC01, X3CC02, X3CC03, X3CC04, X3CC10
class Demand(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X3CC01')
            pc_member = get_pc_member(conference, request.user.email, 'X3CC02')
            paper = get_paper(conference, kwargs['pk'], 'XCC03')
            try:
                get_review_paper(conference, pc_member, paper, '')
                raise PermissionDenied('Error Code: X3CC04')
            except ObjectDoesNotExist:
                if paper in pc_member.demand.all():
                    pc_member.demand.remove(paper)
                    messages.error(request, 'Remove from your List')
                else:
                    pc_member.demand.add(paper)
                    messages.success(request, 'Add to your List')
                return redirect('conference:review_list', slug=kwargs['slug'])
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X3CC10')
            return redirect('home')


# noinspection PyBroadException
# Error X3CD01, X3CD02, X3CD03, X3CD10, X3CD11, X3CD12, X3CD13, X3CD14, X3CD20
class ReviewPaper(TemplateView):
    template_name = 'view3/review_paper.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X3CD01')
            pc_member = get_pc_member(conference, request.user.email, 'X3CD02')
            record = get_review_paper_by_id(conference, pc_member, kwargs['pk'], 'X3CD03')
            review = False
            if conference.review or owner:
                review = True
            form = ReviewPaperForm(instance=record, review=review)
            attr = {'slug': kwargs['slug'], 'owner': owner, 'form': form, 'review': review, 'record': record}
            return render(request, self.template_name, attr)
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X3CD10')
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X3CD11')
            pc_member = get_pc_member(conference, request.user.email, 'X3CD12')
            record = get_review_paper_by_id(conference, pc_member, kwargs['pk'], 'X3CD13')
            review = False
            if conference.review or owner:
                form = ReviewPaperForm(request.POST, instance=record, review=True)
                if form.is_valid():
                    form.save()
                    record.complete = True
                    record.save(update_fields=['complete'])
                    messages.success(request, 'Successfully save')
                    return redirect('conference:review_list', slug=kwargs['slug'])
                else:
                    messages.error(request, 'Invalid Input. X3CD14')
                review = True
            else:
                messages.error(request, 'Review Submission closed')
            form = ReviewPaperForm(instance=record, review=review)
            attr = {'slug': kwargs['slug'], 'owner': owner, 'form': form, 'review': review, 'record': record}
            return render(request, self.template_name, attr)
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X3CD20')
            return redirect('home')


# noinspection PyBroadException
# Error X3CE01, X3CE02, X3CE03, X3CE10, X3CE11, X3CE12, X3CE13, X3CE20
class ShowReviews(TemplateView):
    template_name = 'view3/show_review.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X3CE01')
            if owner:
                paper = get_paper(conference, kwargs['pk'], 'X3CE02')
                reviews = get_all_review_paper(conference, paper)
                form = ReviewConfirmationForm(instance=paper)
                attr = {'owner': owner, 'slug': kwargs['slug'], 'form': form, 'paper': paper, 'reviews': reviews}
                return render(request, self.template_name, attr)
            else:
                raise PermissionDenied('Permission Denied. Error Code: X3CE03')
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X3CE10')
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X3CE11')
            if owner:
                paper = get_paper(conference, kwargs['pk'], 'X3CE12')
                form = ReviewConfirmationForm(request.POST, instance=paper)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Successfully Updated')
                    return redirect('conference:view_all_paper', slug=kwargs['slug'])
                else:
                    messages.error(request, 'Invalid Input')
                reviews = get_all_review_paper(conference, paper)
                form = ReviewConfirmationForm(instance=paper)
                attr = {'owner': owner, 'slug': kwargs['slug'], 'form': form, 'paper': paper, 'reviews': reviews}
                return render(request, self.template_name, attr)
            else:
                raise PermissionDenied('Permission Denied. Error Code: X3CE13')
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X3CE20')
            return redirect('home')


# noinspection PyBroadException
# Error X3CF01, X3CF02, X3CF10
class ShowAllReview(TemplateView):
    template_name = 'view3/all_review.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X3CF01')
            if owner:
                complete = get_all_review_complete(conference, True)
                incomplete = get_all_review_complete(conference, False)
                attr = {'owner': owner, 'slug': kwargs['slug'], 'complete': complete, 'incomplete': incomplete}
                return render(request, self.template_name, attr)
            else:
                raise PermissionDenied('Permission Denied. Error Code: X3CF02')
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied as msg:
            messages.warning(request, msg)
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X3CF20')
            return redirect('home')
