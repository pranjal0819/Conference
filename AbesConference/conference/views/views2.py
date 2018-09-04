# Paper related view

from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from ..forms import PaperRecordForm, AuthorRecordForm
from ..models import PaperRecord, AuthorRecord, ConferenceRecord, PcMemberRecord, ReviewPaperRecord


class Welcome(TemplateView):
    template_name = 'view2/welcome.html'

    def get(self, request, *args, **kwargs):
        try:
            owner = False
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if request.user == con.owner or request.user.is_staff:
                owner = True
            return render(request, self.template_name, {'owner': owner, 'slug': con})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
        # except Exception:
        #     auth.logout(request)
        #     return redirect('home')


class ViewAllPaper(TemplateView):
    template_name = 'view2/submitted_paper.html'

    def get(self, request, *args, **kwargs):
        try:
            conference = ConferenceRecord.objects.get(slug=kwargs['slug'])
            owner = False
            if request.user == conference.owner or request.user.is_staff:
                owner = True
                li = PaperRecord.objects.filter(conference=conference).order_by('id')
                if not li:
                    messages.error(request, 'Paper is not submitted yet')
            else:
                li = PaperRecord.objects.filter(conference=conference, user=request.user)
                if not li:
                    messages.error(request, 'You have not submitted any paper')
            return render(request, self.template_name, {'owner': owner, 'slug': kwargs['slug'], 'paper_list': li})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')


class ViewDetail(TemplateView):
    template_name = 'view2/paper_detail.html'

    def get(self, request, *args, **kwargs):
        try:
            conference = ConferenceRecord.objects.get(slug=kwargs['slug'])
            owner = False
            paper_user = False
            view = False
            pc_users = None
            obj = PaperRecord.objects.get(conference=conference, pk=kwargs['pk'])
            try:
                pc_user = PcMemberRecord.objects.get(pcCon=conference, pcEmail=request.user.email)
                view = True
                ReviewPaperRecord.objects.get(reviewUser=pc_user, paper=obj)
                pc_member = True
            except ObjectDoesNotExist:
                pc_member = False
            if request.user == conference.owner or request.user.is_staff:
                owner = True
                pc_users = PcMemberRecord.objects.filter(pcCon=conference, demand=obj)
            elif obj.user == request.user:
                paper_user = True
            elif pc_member or view:
                pass
            else:
                raise PermissionDenied
            attr = {'owner': owner,
                    'slug': kwargs['slug'],
                    'paper_user': paper_user,
                    'pc_member': pc_member,
                    'paper_record': obj,
                    'pc_users': pc_users}
            return render(request, self.template_name, attr)
        except ObjectDoesNotExist:
            messages.error(request, 'Paper Not Found')
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')


class SubmitPaper(TemplateView):
    template = 'view2/paper_submission.html'

    def get(self, request, *args, **kwargs):
        try:
            paper_form = PaperRecordForm()
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            owner = False
            if con.owner == request.user or request.user.is_staff:
                owner = True
            if not con.submission:
                messages.error(request, 'Submission Closed')
            return render(request, self.template, {'owner': owner, 'slug': kwargs['slug'], 'paper_form': paper_form})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')

    def post(self, request, **kwargs):
        try:
            paper_form = PaperRecordForm(request.POST, request.FILES)
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            owner = False
            try:
                if paper_form.is_valid():
                    if con.submission or (con.owner == request.user) or request.user.is_staff:
                        user = request.user
                        if (con.owner == request.user) or request.user.is_staff:
                            owner = True
                            user = User.objects.get(username=request.POST['user'])
                        temp = paper_form.save(commit=False)
                        temp.user = user
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
                                    obj = AuthorRecord.objects.create(name=nam, email=eml, mobileNumber=mob,
                                                                      country=cou, organization=org, webPage=url)
                                    temp.author.add(obj.id)
                        except Exception:
                            pass
                        messages.success(request, 'Paper submitted successfully')
                        return redirect("conference:view_all_paper", slug=kwargs['slug'])
                    else:
                        paper_form = PaperRecordForm()
                        messages.error(request, 'Submission closed')
                else:
                    paper_form = PaperRecordForm()
                    messages.error(request, 'Retry')
            except ObjectDoesNotExist:
                messages.error(request, 'Invalid User Name')
            return render(request, self.template, {'owner': owner, 'slug': kwargs['slug'], 'paper_form': paper_form})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')


class UpdatePaper(TemplateView):
    template = 'update_paper.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                paper = PaperRecord.objects.get(conference=con, pk=kwargs['pk'])
                li = paper.author.all()
                return render(request, self.template,
                              {'owner': True, 'slug': kwargs['slug'], 'paper_record': paper, 'author_list': li})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')

    def post(self, request, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                paper = PaperRecord.objects.get(conference=con, pk=kwargs['pk'])
                paper.title = request.POST['title']
                paper.keywords = request.POST['keyword']
                paper.abstract = request.POST['abstract']
                try:
                    paper.file = request.FILES['upload']
                    paper.save(update_fields=['title', 'keywords', 'abstract', 'file'])
                except Exception:
                    paper.save(update_fields=['title', 'keywords', 'abstract'])
                messages.success(request, 'Successfully Updated')
                return redirect('conference:view_detail', slug=kwargs['slug'], pk=kwargs['pk'])
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')


class AddAuthor(TemplateView):
    template = 'add_author.html'

    def get(self, request, *args, **kwargs):
        try:
            PaperRecord.objects.get(user=request.user, pk=kwargs['pk'])
            form = AuthorRecordForm()
            return render(request, self.template, {'slug': kwargs['slug'], 'pk': kwargs['pk'], 'author_form': form})
        except ObjectDoesNotExist:
            messages.error(request, 'Permission Denied')
        return redirect('conference:view_detail', **kwargs)

    def post(self, request, **kwargs):
        try:
            author_form = AuthorRecordForm(request.POST)
            if author_form.is_valid():
                con = ConferenceRecord.objects.get(slug=kwargs['slug'])
                try:
                    paper = PaperRecord.objects.get(conference=con, user=request.user, pk=kwargs['pk'])
                    instance = author_form.save()
                    paper.author.add(instance.id)
                    messages.success(request, 'Successfully add Author')
                except ObjectDoesNotExist:
                    messages.error(request, 'Permission Denied')
                return redirect('conference:view_detail', **kwargs)
            else:
                author_form = AuthorRecordForm()
                return render(request, self.template,
                              {'slug': kwargs['slug'], 'pk': kwargs['pk'], 'author_form': author_form})
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')


class UpdateAuthor(TemplateView):
    template = 'update_author.html'

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                author = AuthorRecord.objects.get(pk=kwargs['pk'])
                return render(request, self.template, {'owner': True, 'slug': kwargs['slug'], 'author': author})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')

    def post(self, request, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
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
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')


class DeletePaper(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            con = ConferenceRecord.objects.get(slug=kwargs['slug'])
            if con.owner == request.user or request.user.is_staff:
                obj = PaperRecord.objects.get(conference=con, pk=kwargs['pk'])
                li = obj.author.all()
                for l in li:
                    l.delete()
                obj.delete()
            else:
                raise PermissionDenied
                # obj = PaperRecord.objects.get(conference=con, user=request.user, pk=kwargs['pk'])
                # list = obj.author.all()
                # for l in list:
                #    l.delete()
                # obj.delete()
            messages.success(request, 'Paper deleted')
            return redirect("conference:view_all_paper", slug=kwargs['slug'])
        except ObjectDoesNotExist:
            messages.error(request, 'Conference Closed or Deleted')
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')
