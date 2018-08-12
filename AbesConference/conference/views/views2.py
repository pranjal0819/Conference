# Paper related view

from django.contrib import messages, auth
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from ..forms import PaperRecordForm, AuthorRecordForm
from ..models import PaperRecord, AuthorRecord, ConferenceRecord


class Welcome2(TemplateView):
    template_name = 'welcome2.html'

    def get(self, request, *args, **kwargs):
        try:
            conference = ConferenceRecord.objects.get(slug=kwargs['slug'])
            return render(request, self.template_name, {'conference': conference})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class ViewAllPaper(TemplateView):
    template_name = 'view_all_paper.html'

    def get(self, request, *args, **kwargs):
        try:
            conference = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if request.user.is_staff:
                li = PaperRecord.objects.filter(conference=conference).order_by('id')
                if not li:
                    messages.error(request, 'Paper is not submitted yet')
            else:
                li = PaperRecord.objects.filter(conference=conference, user=request.user)
                if not li:
                    messages.error(request, 'You have not submitted any paper')
            return render(request, self.template_name, {'slug': kwargs['slug'], 'paperList': li})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class ViewDetail(TemplateView):
    template_name = 'detail.html'

    def get(self, request, *args, **kwargs):
        try:
            conference = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if request.user.is_staff:
                obj = PaperRecord.objects.get(conference=conference, pk=kwargs['pk'])
            else:
                obj = PaperRecord.objects.get(conference=conference, user=request.user, pk=kwargs['pk'])
            li = obj.author.all()
            return render(request, self.template_name, {'slug': kwargs['slug'], 'record': obj, 'authorList': li})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class UpdatePaper(TemplateView):
    template_name = 'update_paper.html'

    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_staff:
                con = ConferenceRecord.objects.get(slug=kwargs['slug'])
                paper = PaperRecord.objects.get(conference=con, pk=kwargs['pk'])
                li = paper.author.all()
                return render(request, self.template_name,
                              {'slug': kwargs['slug'], 'record': paper, 'authorList': li})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            if request.user.is_staff:
                con = ConferenceRecord.objects.get(slug=kwargs['slug'])
                paper = PaperRecord.objects.get(conference=con, pk=kwargs['pk'])
                paper.title = request.POST['title']
                paper.keywords = request.POST['keyword']
                paper.abstract = request.POST['abstract']
                try:
                    paper.file = request.FILES['upload']
                    paper.save(update_fields=['title', 'keywords', 'abstract', 'file'])
                except:
                    paper.save(update_fields=['title', 'keywords', 'abstract'])
                messages.success(request, 'Successfully Updated')
                return redirect('conference:view_detail', slug=kwargs['slug'], pk=kwargs['pk'])
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class UpdateAuthor(TemplateView):
    template_name = 'update_author.html'

    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_staff:
                ConferenceRecord.objects.get(slug=kwargs['slug'])
                author = AuthorRecord.objects.get(pk=kwargs['pk'])
                return render(request, self.template_name, {'slug': kwargs['slug'], 'author': author})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            if request.user.is_staff:
                ConferenceRecord.objects.get(slug=kwargs['slug'])
                author = AuthorRecord.objects.get(pk=kwargs['pk'])
                author.name = request.POST['name']
                author.email = request.POST['email']
                author.mobileNumber = request.POST['mobile']
                author.country = request.POST['country']
                author.organization = request.POST['org']
                author.webPage = request.POST['url']
                author.save(update_fields=['name', 'email', 'mobileNumber', 'country', 'organization', 'webPage'])
                messages.success(request, 'Successfully Updated')
                return redirect('conference:view_all_paper', kwargs['slug'])
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class SubmitPaper(TemplateView):
    template_name = 'submit_paper.html'

    def get(self, request, *args, **kwargs):
        paper_form = PaperRecordForm()
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if not con.submission:
                messages.error(request, 'Submission Closed')
            return render(request, self.template_name, {'slug': kwargs['slug'], 'paper_form': paper_form})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')

    def post(self, request, **kwargs):
        paper_form = PaperRecordForm(request.POST, request.FILES)
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.submission and paper_form.is_valid():
                temp = paper_form.save(commit=False)
                temp.user = request.user
                temp.conference = con
                temp.save()
                try:
                    for i in range(1, 4, 1):
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
                messages.success(request, 'Paper submitted successfully')
                return redirect("conference:view_all_paper", slug=kwargs['slug'])
            else:
                paper_form = PaperRecordForm()
                messages.error(request, 'Submission closed')
            return render(request, self.template_name, {'slug': kwargs['slug'], 'paper_form': paper_form})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class AddAuthor(TemplateView):
    template_name = 'add_author.html'

    def get(self, request, *args, **kwargs):
        author_form = AuthorRecordForm()
        return render(request, self.template_name,
                      {'slug': kwargs['slug'], 'pk': kwargs['pk'], 'author_form': author_form})

    def post(self, request, **kwargs):
        try:
            author_form = AuthorRecordForm(request.POST)
            if author_form.is_valid():
                con = ConferenceRecord.objects.get(slug=kwargs['slug'])
                paper = PaperRecord.objects.get(conference=con, pk=kwargs['pk'])
                instance = author_form.save()
                paper.author.add(instance.id)
                return redirect('conference:view_detail', **kwargs)
            else:
                author_form = AuthorRecordForm()
                atr = {'slug': kwargs['slug'], 'pk': kwargs['pk'], 'author_form': author_form}
                return render(request, self.template_name, atr)
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')


class DeletePaper(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if request.user.is_staff:
                obj = PaperRecord.objects.get(conference=con, pk=kwargs['pk'])
                list = obj.author.all()
                for l in list:
                    l.delete()
                obj.delete()
            else:
                raise PermissionDenied
                # obj = PaperRecord.objects.get(conference=con, user=request.user, pk=kwargs['pk'])
                # list = obj.author.all()
                # for l in list:
                #    l.delete()
                # obj.delete()'''
            messages.success(request, 'Paper deleted')
            return redirect("conference:view_all_paper", slug=kwargs['slug'])
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('conference:welcome')
        except:
            auth.logout(request)
            return redirect('home')
