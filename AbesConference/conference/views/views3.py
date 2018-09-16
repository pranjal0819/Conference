# Reviewer related view

from django.contrib import messages, auth
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from ..models import ReviewPaperRecord, ConferenceRecord, PcMemberRecord, PaperRecord


class AcceptToReview(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            pc_member = PcMemberRecord.objects.get(pcCon=con, pcEmail=request.user.email)
            pc_member.accepted = 5
            pc_member.save(update_fields=['accepted'])
            return redirect('conference:review_list', slug=kwargs['slug'])
        except ObjectDoesNotExist:
            messages.error(request, 'You have not selected as Pc Member')
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
        except Exception:
            auth.logout(request)
            return redirect('home')


class ReviewPaperList(TemplateView):
    template = 'view3/review_paper_list.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            list1 = []
            list2 = []
            list3 = []
            accept = False
            owner = False
            pc_member = None
            if con.owner == request.user:
                owner = True
            try:
                pc_member = PcMemberRecord.objects.get(pcCon=con, pcEmail=request.user.email)
                if pc_member.accepted == 5:
                    accept = True
                    paper_list = PaperRecord.objects.filter(conference=con)
                    for paper in paper_list:
                        try:
                            obj = ReviewPaperRecord.objects.get(reviewCon=con, paper=paper, reviewUser=pc_member)
                            if obj.complete:
                                list2.append(paper)
                            else:
                                list1.append(paper)
                        except ObjectDoesNotExist:
                            list3.append(paper)
                else:
                    raise ObjectDoesNotExist
            except ObjectDoesNotExist:
                messages.error(request, 'You are not a Pc Member')
            return render(request, self.template,
                          {'owner': owner, 'slug': kwargs['slug'], 'accept': accept, 'pc_member': pc_member,
                           'list1': list1, 'list2': list2, 'list3': list3})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')


class Demand(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            pc_member = PcMemberRecord.objects.get(pcCon=con, pcEmail=request.user.email)
            paper = PaperRecord.objects.get(conference=con, pk=kwargs['pk'])
            try:
                ReviewPaperRecord.objects.get(reviewCon=con, paper=paper, reviewUser=pc_member)
                raise PermissionDenied
            except ObjectDoesNotExist:
                if paper in pc_member.demand.all():
                    pc_member.demand.remove(paper)
                    pc_member.totalPaper = pc_member.totalPaper - 1
                    pc_member.save(update_fields=['totalPaper'])
                    messages.error(request, 'Remove from your List')
                else:
                    pc_member.demand.add(paper)
                    pc_member.totalPaper = pc_member.totalPaper + 1
                    pc_member.save(update_fields=['totalPaper'])
                    messages.success(request, 'Add to your List')
                return redirect('conference:review_list', slug=kwargs['slug'])
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


class ReviewPaper(TemplateView):
    template_name = 'review_paper.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            pc_member = PcMemberRecord.objects.get(pcCon=con, pcEmail=request.user.email)
            record = ReviewPaperRecord.objects.get(reviewCon=con, reviewUser=pc_member, pk=kwargs['pk'])
            return render(request, self.template_name, {'slug': kwargs['slug'], 'con': con, 'record': record})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect("home")
            # except Exception:
            # auth.logout(request)
            # return redirect('home')

    def post(self, request, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.review:
                pc_member = PcMemberRecord.objects.get(pcCon=con, pcEmail=request.user.email)
                record = ReviewPaperRecord.objects.get(reviewCon=con, reviewUser=pc_member, pk=kwargs['pk'])
                record.overallEvaluation = request.POST['evaluation']
                record.point = int(request.POST['point'])
                record.remark = request.POST['remark']
                record.save(update_fields=['overallEvaluation', 'point', 'remark'])
                messages.success(request, 'Successfully save')
                return redirect("conference:review_list", slug=kwargs['slug'])
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect("home")
        except PermissionDenied:
            messages.error(request, 'Review Closed')
            return redirect('conference:slug_welcome', slug=kwargs['slug'])
            # except Exception:
            # auth.logout(request)
            # return redirect('home')
