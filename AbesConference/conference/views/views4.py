from django.contrib import messages, auth
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from ..models import ReviewPaperRecord, ConferenceRecord


class ReviewerList(TemplateView):
    template_name = 'review_list.html'

    def get(self, request, slug):
        try:
            con = ConferenceRecord.objects.get(slug=slug)
            if True or con.review:
                list = ReviewPaperRecord.objects.filter(reviewCon=con, reviewUser=request.user)
                return render(request, self.template_name, {'slug': slug, 'paperlist': list})
            else:
                messages.error(request, 'Review Closed')
                return redirect('conference:slug_welcome', slug=slug)
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class ReviewPaper(TemplateView):
    template_name = 'review_paper.html'

    def get(self, request, slug, pk):
        try:
            con = ConferenceRecord.objects.get(slug=slug)
            try:
                record = ReviewPaperRecord.objects.get(reviewCon=con, reviewUser=request.user, pk=pk)
                return render(request, self.template_name, {'slug': slug, 'con': con, 'record': record})
            except ObjectDoesNotExist:
                messages.error(request, 'Invalid Paper')
                return redirect("conference:slug_welcome", slug=slug)
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect("conference:welcome")
        except:
            auth.logout(request)
            return redirect('home')

    def post(self, request, slug, pk):
        try:
            con = ConferenceRecord.objects.get(slug=slug)
            if con.review:
                try:
                    record = ReviewPaperRecord.objects.get(reviewCon=con, reviewUser=request.user, pk=pk)

                    record.overallEvaluation = request.POST['evaluation']
                    record.point = int(request.POST['point'])
                    record.remark = request.POST['remark']
                    record.save(update_fields=['overallEvaluation', 'point', 'remark'])

                    messages.success(request, 'Successfully save')
                    return redirect("conference:review_list", slug=slug)
                except:
                    messages.error(request, 'Invalid Paper')
                    return redirect("conference:view_all_paper", slug=slug)
            else:
                auth.logout(request)
                return redirect('home')
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect("conference:welcome")
        except:
            auth.logout(request)
            return redirect('home')
