# Paper related view

from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.forms import formset_factory
from django.http import FileResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from .views0 import *
from ..forms import PaperRecordForm, AuthorRecordForm, AuthorRecordForm1, ConfirmationForm


# noinspection PyBroadException
# Error Code X2CA01, X2CA10
class Welcome(TemplateView):
    template_name = 'view2/welcome.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2CA01')
            return render(request, self.template_name, {'owner': owner, 'slug': conference})
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2CA10')
            return redirect('home')


# noinspection PyBroadException
# Error Code X2CB01, X2CB10
class ViewAllPaper(TemplateView):
    template_name = 'view2/submitted_paper.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2CB01')
            if owner:
                li = get_all_paper(conference)
            else:
                li = get_all_paper_user(conference, request.user)
            return render(request, self.template_name, {'owner': owner, 'slug': kwargs['slug'], 'paper_list': li})
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2CB10')
            return redirect('home')


# noinspection PyBroadException
# Error Code X2CC01, X2CC02, X2CC03, X2CC04, X2CC05, X2CC10, X2CC11, X2CC12, X2CC13, X2CC14, X2CC20
class ViewDetail(TemplateView):
    template_name = 'view2/paper_detail.html'

    def get(self, request, *args, **kwargs):
        try:
            pc_user_list = None
            paper_user = False
            form = None
            conference, owner = get_conference(request, kwargs['slug'], 'X2CC01')
            paper = get_paper(conference, kwargs['pk'], 'X2CC02')
            if owner:
                paper_user = True
                form = ConfirmationForm()
                pc_user_list = get_all_pc_member_for_paper(conference, paper)
            elif paper.user == request.user:
                paper_user = True
            else:
                try:
                    pc_user = get_pc_member(conference, request.user.email, 'X2CC03')
                    try:
                        get_review_paper(pc_user, paper, 'X2CC04')
                        paper_user = True
                    except Exception:
                        pass
                except ObjectDoesNotExist:
                    raise PermissionDenied
            attr = {'owner': owner,
                    'slug': kwargs['slug'],
                    'paper_user': paper_user,
                    'paper_record': paper,
                    'pc_users': pc_user_list,
                    'form': form}
            return render(request, self.template_name, attr)
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            messages.warning(request, 'Permission Denied. Error Code: X2CC05')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2CC10')
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2CC11')
            paper = get_paper(conference, kwargs['pk'], 'X2CC12')
            if owner:
                paper_user = True
                form = ConfirmationForm(request.POST)
                pc_user_list = get_all_pc_member_for_paper(conference, paper)
                if form.is_valid():
                    confirmation = form.cleaned_data['confirmation']
                    if confirmation == 'delete':
                        # paper.delete()
                        # paper.author.all().delete()
                        messages.success(request, 'Delete Successfully')
                        return redirect('conference:view_all_paper', slug=kwargs['slug'])
                    else:
                        messages.error(request, 'Typing Error, Type "delete" for deleting the paper')
                else:
                    messages.error(request, 'Invalid Input. Error Code X2CC13')
                form = ConfirmationForm()
                attr = {'owner': owner,
                        'slug': kwargs['slug'],
                        'paper_user': paper_user,
                        'paper_record': paper,
                        'pc_users': pc_user_list,
                        'form': form}
                return render(request, self.template_name, attr)
            else:
                raise PermissionDenied
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            messages.warning(request, 'Permission Denied. Error Code: X2CC14')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2CC20')
            return redirect('home')


# noinspection PyBroadException
# Error Code X2CD01, X2CD10, X2CD11, X2CD12, X2CD20
class SubmitPaper(TemplateView):
    template = 'view2/paper_submission.html'
    MAX = 5
    MIN = 2

    def get(self, request, *args, **kwargs):
        try:
            sub = False
            confirmation_form = None
            con, owner = get_conference(request, kwargs['slug'], 'X2CD01')
            if owner or con.submission:
                sub = True
                confirmation_form = ConfirmationForm(user=request.user.username)
            paper_form = PaperRecordForm(sub=sub)
            author_form1 = AuthorRecordForm(sub=sub)
            author_form = formset_factory(AuthorRecordForm1, extra=self.MIN, max_num=self.MAX)
            formset = author_form(form_kwargs={'sub': sub})
            attr = {'owner': owner, 'slug': con, 'open': sub, 'confirmation_form': confirmation_form,
                    'paper_form': paper_form, 'form1': author_form1, 'formset': formset}
            return render(request, self.template, attr)
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2CD10')
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            sub = False
            confirmation_form = None
            paper_form = PaperRecordForm(request.POST, request.FILES, sub=True)
            author_form1 = AuthorRecordForm(request.POST, sub=True)
            author_form = formset_factory(AuthorRecordForm1, extra=self.MIN, max_num=self.MAX)
            formset = author_form(request.POST, form_kwargs={'sub': True})
            con, owner = get_conference(request, kwargs['slug'], 'X2CD11')
            if paper_form.is_valid() and author_form1.is_valid() and formset.is_valid():
                if con.submission or owner:
                    user = request.user
                    if owner:
                        try:
                            confirmation_form = ConfirmationForm(request.POST, user=request.user.username)
                            if confirmation_form.is_valid():
                                user = User.objects.get(username=confirmation_form.cleaned_data['confirmation'])
                            else:
                                raise ObjectDoesNotExist
                        except ObjectDoesNotExist:
                            messages.error(request, 'Invalid User Name')
                    temp = paper_form.save(commit=False)
                    temp.user = user
                    temp.conference = con
                    temp.save()
                    temp.author.add(author_form1.save())
                    for form in formset:
                        try:
                            if form.cleaned_data['name']:
                                temp.author.add(form.save())
                        except Exception:
                            pass
                    messages.success(request, 'Paper submitted successfully')
                    return redirect('conference:view_all_paper', slug=kwargs['slug'])
                else:
                    messages.error(request, 'Submission closed')
            else:
                messages.error(request, 'Invalid Input. Try Again. Error Code: X2CD12')
            if con.submission or owner:
                sub = True
                confirmation_form = ConfirmationForm(user=request.user.username)
            paper_form = PaperRecordForm(sub=sub)
            author_form1 = AuthorRecordForm(sub=sub)
            author_form = formset_factory(AuthorRecordForm1, extra=self.MIN, max_num=self.MAX)
            formset = author_form(form_kwargs={'sub': sub})
            attr = {'owner': owner, 'slug': con, 'open': sub, 'confirmation_form': confirmation_form,
                    'paper_form': paper_form, 'form1': author_form1, 'formset': formset}
            return render(request, self.template, attr)
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2CD20')
            return redirect('home')


# noinspection PyBroadException
# Error Code X2CE01, X2CE02, X2CE03, X2CE04, X2CE05, X2CE10
class DownloadPaper(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2CE01')
            paper = get_paper(conference, kwargs['pk'], 'X2CE02')
            if paper.user == request.user or owner:
                response = FileResponse(paper.file)
                response['Content-Disposition'] = 'inline; filename={title}.pdf'.format(
                    title=kwargs['slug'] + "-" + str(kwargs['pk']))
                return response
            else:
                pc_member = get_pc_member(conference, request.user.email, 'X2CE03')
                if pc_member.accepted == 5:
                    get_review_paper(pc_member, pc_member, 'X2CE04')
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
            messages.warning(request, 'Permission Denied. Error Code: X2CE05')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2CE10')
            return redirect('home')


# noinspection PyBroadException
# Error Code X2CF01, X2CF02, X2CF03, X2CF10, X2CF11, X2CF12, X2CF13, X2CF20
class UpdatePaper(TemplateView):
    template = 'view2/update_paper.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2CF01')
            if owner:
                paper = get_paper(conference, kwargs['pk'], 'X2CF02')
                form = PaperRecordForm(instance=paper, sub=True)
                return render(request, self.template,
                              {'owner': owner, 'slug': kwargs['slug'], 'paper': paper, 'form': form})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            messages.warning(request, 'Permission Denied. Error Code: X2CF03')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2CF10')
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2CF11')
            if owner:
                paper = get_paper(conference, kwargs['pk'], 'X2CF12')
                form = PaperRecordForm(request.POST, request.FILES, instance=paper, sub=True)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Successfully Updated')
                    return redirect('conference:view_detail', slug=kwargs['slug'], pk=kwargs['pk'])
                else:
                    messages.error(request, 'Invalid Input. Try Again. Error Code: X2CF05')
                form = PaperRecordForm(instance=paper, sub=True)
                return render(request, self.template,
                              {'owner': owner, 'slug': kwargs['slug'], 'paper': paper, 'form': form})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            messages.warning(request, 'Permission Denied. Error Code: X2CF13')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2CF20')
            return redirect('home')


# noinspection PyBroadException
# Error Code X2CG01, X2CG02, X2CG03, X2CG10, X2CG11, X2CG12, X2CG13, X2CG20
class AddAuthor(TemplateView):
    template = 'view2/add_author.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2CG01')
            paper = get_paper(conference, kwargs['pk'], 'X2CG02')
            if paper.user == request.user:
                form = AuthorRecordForm(sub=conference.submission)
                return render(request, self.template, {'slug': kwargs['slug'], 'pk': kwargs['pk'], 'form': form})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            messages.warning(request, 'Permission Denied. Error Code: X2CG03')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2CG10')
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2CG11')
            paper = get_paper(conference, kwargs['pk'], 'X2CG04')
            if paper.user == request.user:
                form = AuthorRecordForm(request.POST, sub=conference.submission)
                if form.is_valid():
                    instance = form.save()
                    paper.author.add(instance)
                    messages.success(request, 'Successfully add Author')
                    return redirect('conference:view_detail', **kwargs)
                else:
                    messages.error(request, 'Invalid Input. Try Again. Error Code: X2CG12')
                form = AuthorRecordForm(sub=conference.submission)
                return render(request, self.template, {'slug': kwargs['slug'], 'pk': kwargs['pk'], 'form': form})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            messages.warning(request, 'Permission Denied. Error Code: X2CG13')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2CG20')
            return redirect('home')


# noinspection PyBroadException
# Error Code X2CH01, X2CH02, X2CH03, X2CH04, X2CH10, X2CH11, X2CH12, X2CH13, X2CH14, X2CH15, X2CH20
class UpdateAuthor(TemplateView):
    template = 'view2/update_author.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2CH01')
            paper = get_paper(conference, kwargs['paper'], 'X2CH02')
            if paper.user == request.user or owner:
                author = get_author(kwargs['pk'], 'X2CH03')
                form = AuthorRecordForm(instance=author, sub=conference.submission)
                return render(request, self.template,
                              {'owner': True, 'slug': kwargs['slug'], 'author': author, 'form': form})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            messages.warning(request, 'Permission Denied. Error Code: X2CH04')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2CH10')
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2CH11')
            paper = get_paper(conference, kwargs['paper'], 'X2CH12')
            if paper.user == request.user or owner:
                author = get_author(kwargs['pk'], 'X2CH13')
                form = AuthorRecordForm(request.POST, instance=author, sub=conference.submission)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Successfully Updated')
                    return redirect('conference:view_detail', slug=kwargs['slug'], pk=kwargs['paper'])
                else:
                    messages.error(request, 'Invalid Input. Try Again. Error Code: X2CH14')
                form = AuthorRecordForm(sub=conference.submission)
                return render(request, self.template,
                              {'owner': True, 'slug': kwargs['slug'], 'author': author, 'form': form})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            messages.warning(request, 'Permission Denied. Error Code: X2CH15')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2CH20')
            return redirect('home')
