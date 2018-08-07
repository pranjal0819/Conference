from django.contrib import messages, auth
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.core.exceptions import ObjectDoesNotExist
from ..forms import AuthorRecordForm, PaperRecordForm, ReviewPaperForm
from ..models import PaperRecord, AuthorRecord, ReviewPaperRecord


class ReviewList(TemplateView):
    template_name = 'review_list.html'

    def get(self, request):
        list = ReviewPaperRecord.objects.all()
        return render(request, self.template_name, {'list': list})


class ReviewPaper(TemplateView):
    template_name = 'review_paper.html'

    def get(self, request, pk):
        try:
            form = ReviewPaperForm()
            record = ReviewPaperRecord.objects.get(user=request.user, pk=pk)
            return render(request, self.template_name, {'form': form, 'record': record})
        except ObjectDoesNotExist:
            redirect("conference:view_all_paper")

    def post(self, request, pk):
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


class SelectUser(TemplateView):
    template_name = 'userlist.html'

    def get(self, request, pk):
        try:
            if request.user.is_staff:
                paper = PaperRecord.objects.get(pk=pk)
                userlist = auth.models.User.objects.exclude(username=paper.user).filter(is_superuser=False)
                list1 = []
                for user in userlist:
                    try:
                        ReviewPaperRecord.objects.get(user=user, paper=paper)
                        list = [user,True]
                        list1.append(list)
                    except:
                        list = [user,False]
                        list1.append(list)
                print(list1)
                return render(request, self.template_name, {'paper': paper, 'userlist': list1})
            else:
                messages.error(request, "Lot of Error")
                redirect("conference:welcome")
        except:
            messages.error(request, "Lot of error")
            redirect("conference:view_all_paper")


class SelectedUser(TemplateView):

    def get(self, request, paper_pk, user_pk):
        if request.user.is_staff:
            try:
                user = auth.models.User.objects.get(pk=user_pk)
                paper = PaperRecord.objects.get(pk=paper_pk)
                try:
                    ReviewPaperRecord.objects.get(user=user, paper=paper)
                    messages.error(request, "Already Assign this user")
                except:
                    instance = ReviewPaperRecord.objects.create(user=user, paper=paper, overallEvaluation='', remark='',
                                                                point=0)
                    instance.save()
                    messages.success(request, "Successfuly record save")
            except:
                messages.error(request, "Please Try again")
            return redirect("conference:view_all_paper")
        else:
            messages.error(request, "You are not a Chair Person")
            return redirect("conference:welcome")
