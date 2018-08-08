from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from ..forms import ReviewPaperForm
from ..models import ReviewPaperRecord, ConferenceRecord


class ReviewerList(TemplateView):
    template_name = 'review_list.html'

    def get(self, request, slug):
        try:
            con = ConferenceRecord.objects.get(slug=slug)
            if con.review:
                list = ReviewPaperRecord.objects.filter(reviewCon=con, reviewUser=request.user)
                return render(request, self.template_name, {'paperList': list})
            else:
                messages.error(request, 'Review Closed')
                return redirect('conference:slug_welcome', slug=slug)
        except:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')


class ReviewPaper(TemplateView):
    template_name = 'review_paper.html'

    def get(self, request, slug, pk):
        try:
            form = ReviewPaperForm()
            record = ReviewPaperRecord.objects.get(user=request.user, pk=pk)
            return render(request, self.template_name, {'form': form, 'record': record})
        except ObjectDoesNotExist:
            redirect("conference:view_all_paper")

    def post(self, request, slug, pk):
        try:
            form = ReviewPaperForm(request.POST)
            record = ReviewPaperRecord.objects.get(user=request.user, pk=pk)
            if form.is_valid():
                record.overallEvaluation = form.cleaned_data['overallEvaluation']
                record.point = form.cleaned_data['point']
                record.remark = form.cleaned_data['remark']
                record.save(update_fields=['overallEvaluation', 'point', 'remark'])
                messages.success(request, "Succesfuly save")
                return redirect("conference:welcome")
            else:
                messages.error(request, "Data not save")
                return redirect("conference:welcome")
        except ObjectDoesNotExist:
            redirect("conference:view_all_paper")
