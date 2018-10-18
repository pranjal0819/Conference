# Reviewer related view

from django.contrib import messages, auth
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from .views0 import *
from ..forms import ReviewPaperForm


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
        # except Exception:
        #     auth.logout(request)
        #     messages.error(request, 'Error Code: X3CD10')
        #     return redirect('home')

    def post(self, request, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X3CD11')
            pc_member = get_pc_member(conference, request.user.email, 'X3CD12')
            record = get_review_paper_by_id(conference, pc_member, kwargs['pk'], 'X3CD13')
            review = False
            if conference.review or owner:
                review = True
                form = ReviewPaperForm(request.POST, instance=record, review=True)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Successfully save')
                else:
                    messages.error(request, 'Invalid Input. X3CD14')
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
class ShowReviews(TemplateView):
    template_name = 'view3/show_review.html'

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
        except PermissionDenied:
            auth.logout(request)
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
        except PermissionDenied:
            auth.logout(request)
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')


class ShowAllReview(TemplateView):
    template_name = 'view3/all_review.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                obj = ReviewPaperRecord.objects.filter(reviewCon=con)
                return render(request, self.template_name, {'owner': True, 'slug': kwargs['slug'], 'reviews': obj})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')


class ShowAllPendingReview(TemplateView):
    template_name = 'view3/all_pending_review.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                obj = ReviewPaperRecord.objects.filter(reviewCon=con, complete=False)
                return render(request, self.template_name, {'owner': True, 'slug': kwargs['slug'], 'reviews': obj})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')


class AcceptPaper(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            pc_member = PcMemberRecord.objects.get(pcCon=con, pcEmail=request.user.email)
            record = ReviewPaperRecord.objects.get(reviewCon=con, reviewUser=pc_member, pk=kwargs['pk'])
            record.accepted = 5
            record.save(update_fields=['accepted'])
            return redirect('conference:review_paper', slug=kwargs['slug'], pk=kwargs['pk'])
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect("home")
            # except Exception:
            # auth.logout(request)
            # return redirect('home')


class RejectPaper(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            pc_member = PcMemberRecord.objects.get(pcCon=con, pcEmail=request.user.email)
            record = ReviewPaperRecord.objects.get(reviewCon=con, reviewUser=pc_member, pk=kwargs['pk'])
            if record.accepted == 3:
                record.accepted = 0
                record.save(update_fields=['accepted'])
            return redirect('conference:review_paper', slug=kwargs['slug'], pk=kwargs['pk'])
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect("home")
            # except Exception:
            # auth.logout(request)
            # return redirect('home')
