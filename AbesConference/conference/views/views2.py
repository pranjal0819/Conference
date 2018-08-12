from django.contrib import messages, auth
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from ..forms import AuthorRecordForm, PaperRecordForm
from ..models import PaperRecord, AuthorRecord, ConferenceRecord


class Welcome2(TemplateView):
    template_name = 'welcome2.html'

    def get(self, request, slug):
        try:
            conference = ConferenceRecord.objects.get(slug=slug)
            return render(request, self.template_name, {'conference': conference})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class ViewAllPaper(TemplateView):
    template_name = 'view_all_paper.html'

    def get(self, request, slug):
        try:
            conference = ConferenceRecord.objects.get(slug=slug)
            if request.user.is_staff:
                list = PaperRecord.objects.filter(conference=conference).order_by('id')
                if not list:
                    messages.error(request, 'Paper is not submitted yet')
            else:
                list = PaperRecord.objects.filter(conference=conference, user=request.user)
                if not list:
                    messages.error(request, 'You have not submitted any paper')
            return render(request, self.template_name, {'slug': slug, 'paperlist': list})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class ViewDetail(TemplateView):
    template_name = 'detail.html'

    def get(self, request, slug, pk):
        try:
            conference = ConferenceRecord.objects.get(slug=slug)
            if request.user.is_staff:
                obj = PaperRecord.objects.get(conference=conference, pk=pk)
            else:
                obj = PaperRecord.objects.get(conference=conference, user=request.user, pk=pk)
            list = obj.author.all()
            return render(request, self.template_name, {'slug': slug, 'record': obj, 'authorlist': list})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class UpdatePaper(TemplateView):
    template_name = 'update.html'

    def get(self, request, slug, pk):
        try:
            if request.user.is_staff:
                con = ConferenceRecord.objects.get(slug=slug)
                paper = PaperRecord.objects.get(conference=con, pk=pk)
                list = paper.author.all()
                return render(request, self.template_name, {'slug': slug, 'record': paper, 'authorlist': list})
            else:
                raise PermissionError
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')

    def post(self, request, slug, pk):
        try:
            if request.user.is_staff:
                con = ConferenceRecord.objects.get(slug=slug)
                paper = PaperRecord.objects.get(conference=con, pk=pk)
                paper.title = request.POST['title']
                paper.keywords = request.POST['keyword']
                paper.abstract = request.POST['abstract']
                try:
                    paper.file = request.FILES['upload']
                    paper.save(update_fields=['title', 'keywords', 'abstract', 'file'])
                except:
                    paper.save(update_fields=['title', 'keywords', 'abstract'])
                messages.success(request, 'Successfully Updated')
                return redirect('conference:view_detail', slug=slug, pk=pk)
            else:
                raise PermissionError
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class SubmitPaper(TemplateView):
    template_name = 'submit_paper.html'

    def get(self, request, slug):
        authorform = AuthorRecordForm()
        paperform = PaperRecordForm()
        try:
            con = ConferenceRecord.objects.get(slug=slug)
            if not con.submission:
                messages.error(request, 'Submission Closed')
            attr = {'slug': slug, 'authorform': authorform, 'paperform': paperform}
            return render(request, self.template_name, attr)
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')

    def post(self, request, slug):
        paperform = PaperRecordForm(request.POST, request.FILES)
        try:
            con = ConferenceRecord.objects.get(slug=slug)
            if con.submission and paperform.is_valid():
                temp = paperform.save(commit=False)
                temp.user = request.user
                temp.conference = con
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
                                                              organization=org, webPage=url)
                            temp.author.add(obj.id)
                except:
                    pass
                messages.success(request, 'Paper submited successfuly')
                return redirect("conference:view_all_paper", slug=slug)
            else:
                paperform = PaperRecordForm()
                messages.error(request, 'Submission closed')
            return render(request, self.template_name, {'slug': slug, 'paperform': paperform})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class DeletePaper(TemplateView):

    def get(self, request, slug, pk):
        try:
            con = ConferenceRecord.objects.get(slug=slug)
            if request.user.is_staff:
                obj = PaperRecord.objects.get(conference=con, pk=pk)
                list = obj.author.all()
                for l in list:
                    l.delete()
                obj.delete()
            else:
                raise PermissionError
                '''obj = PaperRecord.objects.get(conference=con, user=request.user, pk=pk)
                list = obj.author.all()
                for l in list:
                    l.delete()
                obj.delete()'''
            messages.success(request, 'Paper deleted')
            return redirect("conference:view_all_paper", slug=slug)
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')
