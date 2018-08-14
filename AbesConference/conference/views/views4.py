# Reviewer related view

from django.contrib import messages, auth
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from ..models import ReviewPaperRecord, ConferenceRecord, PcMemberRecord


class ReviewPaperList(TemplateView):
    template_name = 'review_paper_list.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            try:
                pc_member = PcMemberRecord.objects.get(pcCon=con, pcEmail=request.user.email)
                li = ReviewPaperRecord.objects.filter(reviewCon=con, reviewUser=pc_member)
                return render(request, self.template_name, {'slug': kwargs['slug'], 'paper_list': li})
            except ObjectDoesNotExist:
                li = None
                return render(request, self.template_name, {'slug': kwargs['slug'], 'paper_list': li})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except Exception:
            auth.logout(request)
            return redirect('home')


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
            return redirect("conference:welcome")
        except:
            auth.logout(request)
            return redirect('home')

    def post(self, request, *args, **kwargs):
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
            return redirect("conference:welcome")
        except:
            auth.logout(request)
            return redirect('home')
