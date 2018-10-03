# Paper related view

from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.forms import formset_factory
from django.http import FileResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from .views0 import *
from ..forms import PaperRecordForm, AuthorRecordForm, AuthorRecordForm1
from ..models import PaperRecord, AuthorRecord, ConferenceRecord


# noinspection PyBroadException
# Error Code X0AA01, X0AA10
class Welcome(TemplateView):
    template_name = 'view2/welcome.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X0AA01')
            return render(request, self.template_name, {'owner': owner, 'slug': conference})
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except Exception:
            messages.error(request, 'Error Code: X0AA10')
            # auth.logout(request)
            return redirect('home')


# noinspection PyBroadException
# Error Code X0AB01, X0AB10
class ViewAllPaper(TemplateView):
    template_name = 'view2/submitted_paper.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X0AB01')
            if owner:
                li = get_all_paper_chair(conference)
            else:
                li = get_all_paper_user(conference, request.user)
            return render(request, self.template_name, {'owner': owner, 'slug': kwargs['slug'], 'paper_list': li})
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except Exception:
            messages.error(request, 'Error Code: X0AB10')
            # auth.logout(request)
            return redirect('home')


# noinspection PyBroadException
# Error Code X0AC01, X0AC02, X0AC10
class ViewDetail(TemplateView):
    template_name = 'view2/paper_detail.html'

    def get(self, request, *args, **kwargs):
        try:
            pc_user_list = None
            paper_user = False
            conference, owner = get_conference(request, kwargs['slug'], 'X0AC01')
            paper = get_paper(conference, kwargs['pk'], 'X0AC02')
            if owner:
                paper_user = True
                pc_user_list = get_all_pc_member_for_paper(conference, paper)
            elif paper.author == request.user:
                paper_user = True
            else:
                try:
                    pc_user = get_pc_member(conference, request.user.email, 'X0AC03')
                    try:
                        get_review_paper(pc_user, paper, 'X0AC04')
                        paper_user = True
                    except Exception:
                        pass
                except ObjectDoesNotExist:
                    raise PermissionDenied
            attr = {'owner': owner,
                    'slug': kwargs['slug'],
                    'paper_user': paper_user,
                    'paper_record': paper,
                    'pc_users': pc_user_list}
            return render(request, self.template_name, attr)
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            return redirect('home')
        except Exception:
            messages.error(request, 'Error Code: X0AC10')
            # auth.logout(request)
            return redirect('home')


# noinspection PyBroadException
# Error Code X0AD01, X0AD02, X0AD03, X0AD10, X0AD11
class SubmitPaper(TemplateView):
    template = 'view2/paper_submission.html'
    data = {'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '5'}

    def get(self, request, *args, **kwargs):
        try:
            sub = False
            con, owner = get_conference(request, kwargs['slug'], 'X0AD01')
            if owner or con.submission:
                sub = True
            paper_form = PaperRecordForm(sub=sub)
            author_form1 = AuthorRecordForm(sub=sub)
            author_form = formset_factory(AuthorRecordForm1, extra=2)
            formset = author_form(form_kwargs={'sub': sub})
            attr = {'owner': owner, 'slug': con, 'open': sub,
                    'paper_form': paper_form, 'form1': author_form1, 'formset': formset}
            return render(request, self.template, attr)
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        # except Exception:
        #     messages.error(request, 'Error Code: X0AD10')
        #     # auth.logout(request)
        #     return redirect('home')

    def post(self, request, **kwargs):
        try:
            sub = False
            paper_form = PaperRecordForm(request.POST, request.FILES, sub=True)
            author_form1 = AuthorRecordForm(request.POST, sub=True)
            author_form = formset_factory(AuthorRecordForm1, extra=2)
            formset = author_form(request.POST, form_kwargs={'sub': True})
            con, owner = get_conference(request, kwargs['slug'], 'X0AD02')
            if paper_form.is_valid() and author_form1.is_valid() and formset.is_valid():
                if con.submission or owner:
                    user = request.user
                    if owner:
                        try:
                            user = User.objects.get(username=request.POST['user'])
                        except ObjectDoesNotExist:
                            messages.error(request, 'Invalid User Name')
                    temp = paper_form.save(commit=False)
                    temp.user = user
                    temp.conference = con
                    temp.save()
                    temp.author.add(author_form1.save())
                    for form in formset:
                        if form.cleaned_data['name']:
                            temp.author.add(form.save())
                    messages.success(request, 'Paper submitted successfully')
                    return redirect("conference:view_all_paper", slug=kwargs['slug'])
                else:
                    messages.error(request, 'Submission closed')
            else:
                messages.error(request, 'Invalid Input. Try Again. Error Code: X0AD03')
            if con.submission or owner:
                sub = True
            paper_form = PaperRecordForm(sub=sub)
            author_form1 = AuthorRecordForm(sub=sub)
            author_form = formset_factory(AuthorRecordForm1, extra=2)
            formset = author_form(form_kwargs={'sub': sub})
            attr = {'owner': owner, 'slug': con, 'open': sub,
                    'paper_form': paper_form, 'form1': author_form1, 'formset': formset}
            return render(request, self.template, attr)
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except Exception:
            messages.error(request, 'Error Code: X0AD11')
            # auth.logout(request)
            return redirect('home')


# noinspection PyBroadException
# Error Code X0AE01, X0AE02, X0AE03, X0AE04, X0AE11
class DownloadPaper(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X0AE01')
            paper = get_paper(conference, kwargs['pk'], 'X0AE02')
            if paper.user == request.user or owner:
                response = FileResponse(paper.file)
                response['Content-Disposition'] = 'inline; filename={title}.pdf'.format(
                    title=kwargs['slug'] + "-" + str(kwargs['pk']))
                return response
            else:
                pc_member = get_pc_member(conference, request.user.email, 'X0AE03')
                if pc_member.accepted == 5:
                    get_review_paper(pc_member, pc_member, 'X0AE04')
                    response = FileResponse(paper.file)
                    response['Content-Disposition'] = 'inline; filename={title}.pdf'.format(
                        title=kwargs['slug'] + "-" + str(kwargs['pk']))
                    return response
                raise PermissionDenied
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            return redirect('home')
        except Exception:
            messages.error(request, 'Error Code: X0AE11')
            # auth.logout(request)
            return redirect('home')


# noinspection PyBroadException
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
        except PermissionDenied:
            auth.logout(request)
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
        except PermissionDenied:
            auth.logout(request)
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
        except PermissionDenied:
            auth.logout(request)
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
        except PermissionDenied:
            auth.logout(request)
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
        except PermissionDenied:
            auth.logout(request)
            return redirect('home')
            # except Exception:
            # auth.logout(request)
            # return redirect('home')
