from django.contrib import messages, auth
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.core.exceptions import ObjectDoesNotExist
from .forms import AuthorRecordForm, PaperRecordForm, ReviewPaperForm
from .models import PaperRecord, AuthorRecord, ReviewPaperRecord


# Create your views here.
class Welcome(TemplateView):
    template_name = 'welcome.html'

    def get(self, request):
        return render(request, self.template_name, {})


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


class ViewAllPaper(TemplateView):
    template_name = 'view_all_paper.html'

    def get(self, request):
        if request.user.is_staff:
            list = PaperRecord.objects.all().order_by('id')
            if not list:
                messages.error(request, "Paper is not submited yet")
        else:
            list = PaperRecord.objects.filter(user=request.user)
            if not list:
                messages.error(request, "You have not submited any paper")
        return render(request, self.template_name, {'paperlist': list})


class SelectUser(TemplateView):
    template_name = 'userlist.html'

    def get(self, request, pk):
        try:
            if request.user.is_staff:
                paper = PaperRecord.objects.get(pk=pk)
                userlist = auth.models.User.objects.exclude(username=paper.user).filter(is_superuser=False)
                list1 = []
                list2 = []
                for user in userlist:
                    try:
                        ReviewPaperRecord.objects.get(user=user, paper=paper)
                        list1.append(user)
                    except:
                        list2.append(user)
                attr = {'userlist': userlist, 'paper': paper, 'list1': list1, 'list2': list2}
                return render(request, self.template_name, attr)
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


class ViewDetail(TemplateView):
    template_name = 'detail.html'

    def get(self, request, pk):
        try:
            if request.user.is_staff:
                obj = PaperRecord.objects.get(pk=pk)
            else:
                obj = PaperRecord.objects.get(user=request.user, pk=pk)
            list = obj.author.all()
        except:
            obj = None
            list = None
            messages.error(request, "Lot of Error")
            return redirect("conference:welcome")
        return render(request, self.template_name, {'record': obj, 'authorlist': list})


class SubmitPaper(TemplateView):
    template_name = 'submit_paper.html'

    def get(self, request):
        authorform = AuthorRecordForm()
        paperform = PaperRecordForm()
        attr = {'authorform': authorform,
                'paperform': paperform}
        return render(request, self.template_name, attr)

    def post(self, request):
        paperform = PaperRecordForm(request.POST, request.FILES)
        if paperform.is_valid():
            temp = paperform.save(commit=False)
            temp.status = False
            temp.user = request.user
            temp.save()
            try:
                for i in range(1, 10, 1):
                    j = str(i)
                    nam = request.POST['name' + j]
                    eml = request.POST['email' + j]
                    mob = request.POST['mobile' + j]
                    cou = request.POST['country' + j]
                    org = request.POST['org' + j]
                    url = request.POST['url' + j]
                    if nam is not "":
                        obj = AuthorRecord.objects.create(name=nam, email=eml, mobileNumber=mob, country=cou,
                                                          organization=org, webpage=url)
                        temp.author.add(obj.id)
            except:
                pass
            messages.success(request, "Paper submited successfuly")
            return redirect("conference:submit_paper")
        else:
            messages.error(request, "Lot of Error")
            return redirect("conference:welcome")
        return render(request, self.template_name, {'paperform': None})


class DeletePaper(TemplateView):

    def get(self, request, pk):
        try:
            if request.user.is_staff:
                obj = PaperRecord.objects.get(pk=pk)
            else:
                obj = PaperRecord.objects.get(user=request.user, pk=pk)
            list = obj.author.all()
            for l in list:
                l.delete()
            obj.delete()
            messages.success(request, "Paper deleted")
        except:
            messages.error(request, "Lot of error")
            return redirect("conference:welcome")
        return redirect("conference:view_all_paper")
