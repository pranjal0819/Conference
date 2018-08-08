from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from ..models import PaperRecord, ReviewPaperRecord, ConferenceRecord


class SelectUser(TemplateView):
    template_name = 'userlist.html'

    def get(self, request, slug, pk):
        if True:
            con = ConferenceRecord.objects.get(slug=slug)
            if request.user.is_staff and con.review:
                paper = PaperRecord.objects.get(conference=con, pk=pk)
                userlist = User.objects.exclude(username=paper.user).filter(is_superuser=False)
                list1 = []
                for user in userlist:
                    try:
                        ReviewPaperRecord.objects.get(reviewUser=user, paper=paper)
                        list = [user, True]
                        list1.append(list)
                    except:
                        list = [user, False]
                        list1.append(list)
                print("Hello",list1)
                return render(request, self.template_name, {'slug':slug, 'paper': paper, 'userlist': list1})
            else:
                messages.error(request, 'Review Closed or Invalid User')
                return redirect("conference:slug_welcome", slug=slug)
        else:
            messages.error(request, 'Conference Closed or Deleted or Invalid Paper')
            return redirect("conference:welcome")


class SelectedUser(TemplateView):

    def get(self, request, slug, paper_pk, user_pk):
        try:
            con = ConferenceRecord.objects.get(slug=slug)
            if request.user.is_staff and con.review:
                user = User.objects.get(pk=user_pk)
                paper = PaperRecord.objects.get(conference=con, pk=paper_pk)
                try:
                    ReviewPaperRecord.objects.get(reviewUser=user, paper=paper)
                    messages.error(request, 'Already Assign this user')
                except:
                    instance = ReviewPaperRecord.objects.create(reviewUser=user, paper=paper, reviewCon=con,
                                                                overallEvaluation='', remark='', point=0)
                    instance.save()
                    messages.success(request, 'Successfuly record save')
                return redirect("conference:select_user", slug=slug, pk=paper_pk)
            else:
                messages.error(request, 'Review Closed or Invalid User')
                return redirect("conference:slug_welcome", slug=slug)
        except:
            messages.error(request, 'Conference Closed or Deleted or Invalid Paper')
            return redirect("conference:welcome")