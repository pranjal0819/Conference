from django.contrib import messages, auth
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.core.exceptions import ObjectDoesNotExist
from conference.forms import AuthorRecordForm, PaperRecordForm, ReviewPaperForm
from conference.models import PaperRecord, AuthorRecord, ReviewPaperRecord


class Welcome(TemplateView):
    template_name = 'welcome.html'

    def get(self, request):
        return render(request, self.template_name, {})


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
