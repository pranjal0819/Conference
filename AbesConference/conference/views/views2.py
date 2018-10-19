# Paper related view

from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.forms import formset_factory
from django.http import FileResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from .views0 import *
from ..forms import PaperRecordForm, AuthorRecordForm, AuthorRecordForm1, ConfirmationForm


# noinspection PyBroadException
# Error Code X2BA01, X2BA10
class Welcome(TemplateView):
    template_name = 'view2/welcome.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2BA01')
            try:
                get_pc_member(conference, request.user.email, '')
                pc_member = True
            except PermissionDenied:
                pc_member = False
            return render(request, self.template_name, {'owner': owner, 'slug': conference, 'pc_member': pc_member})
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2BA10')
            return redirect('home')


# noinspection PyBroadException
# Error Code X2BB01, X2BB10
class ViewAllPaper(TemplateView):
    template_name = 'view2/submitted_paper.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2BB01')
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
            messages.error(request, 'Error Code: X2BB10')
            return redirect('home')


# noinspection PyBroadException
# Error Code X2BC01, X2BC02, X2BC03, X2BC04, X2BC05, X2BC10, X2BC11, X2BC12, X2BC13, X2BC14, X2BC20
class ViewDetail(TemplateView):
    template_name = 'view2/paper_detail.html'

    def get(self, request, *args, **kwargs):
        try:
            pc_user_list = None
            paper_user = False
            form = None
            conference, owner = get_conference(request, kwargs['slug'], 'X2BC01')
            paper = get_paper(conference, kwargs['pk'], 'X2BC02')
            if owner:
                paper_user = True
                form = ConfirmationForm()
                pc_user_list = get_all_pc_member_for_paper(conference, paper)
            elif paper.user == request.user:
                paper_user = True
            else:
                try:
                    pc_user = get_pc_member(conference, request.user.email, 'X2BC03')
                    try:
                        get_review_paper(conference, pc_user, paper, 'X2BC04')
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
            messages.warning(request, 'Permission Denied. Error Code: X2BC05')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2BC10')
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2BC11')
            paper = get_paper(conference, kwargs['pk'], 'X2BC12')
            if owner:
                paper_user = True
                form = ConfirmationForm(request.POST)
                pc_user_list = get_all_pc_member_for_paper(conference, paper)
                if form.is_valid():
                    confirmation = form.cleaned_data['confirmation']
                    if confirmation == 'delete':
                        paper.delete()
                        # paper.author.all().delete()
                        messages.success(request, 'Delete Successfully')
                        return redirect('conference:view_all_paper', slug=kwargs['slug'])
                    else:
                        messages.error(request, 'Typing Error, Type "delete" for deleting the paper')
                else:
                    messages.error(request, 'Invalid Input. Error Code X2BC13')
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
            messages.warning(request, 'Permission Denied. Error Code: X2BC14')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2BC20')
            return redirect('home')


# noinspection PyBroadException
# Error Code X2BD01, X2BD10, X2BD11, X2BD12, X2BD20
class SubmitPaper(TemplateView):
    template = 'view2/paper_submission.html'
    MAX = 5
    MIN = 2

    def get(self, request, *args, **kwargs):
        try:
            sub = False
            confirmation_form = None
            con, owner = get_conference(request, kwargs['slug'], 'X2BD01')
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
            messages.error(request, 'Error Code: X2BD10')
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            sub = False
            confirmation_form = None
            paper_form = PaperRecordForm(request.POST, request.FILES, sub=True)
            author_form1 = AuthorRecordForm(request.POST, sub=True)
            author_form = formset_factory(AuthorRecordForm1, extra=self.MIN, max_num=self.MAX)
            formset = author_form(request.POST, form_kwargs={'sub': True})
            con, owner = get_conference(request, kwargs['slug'], 'X2BD11')
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
                messages.error(request, 'Invalid Input. Try Again. Error Code: X2BD12')
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
            messages.error(request, 'Error Code: X2BD20')
            return redirect('home')


# noinspection PyBroadException
# Error Code X2BE01, X2BE02, X2BE03, X2BE04, X2BE05, X2BE10
class DownloadPaper(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2BE01')
            paper = get_paper(conference, kwargs['pk'], 'X2BE02')
            if paper.user == request.user or owner:
                response = FileResponse(paper.file)
                response['Content-Disposition'] = 'inline; filename={title}.pdf'.format(
                    title=kwargs['slug'] + "-" + str(kwargs['pk']))
                return response
            else:
                pc_member = get_pc_member(conference, request.user.email, 'X2BE03')
                if pc_member.accepted == 5:
                    get_review_paper(conference, pc_member, pc_member, 'X2BE04')
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
            messages.warning(request, 'Permission Denied. Error Code: X2BE05')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2BE10')
            return redirect('home')


# noinspection PyBroadException
# Error Code X2BF01, X2BF02, X2BF03, X2BF10, X2BF11, X2BF12, X2BF13, X2BF20
class UpdatePaper(TemplateView):
    template = 'view2/update_paper.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2BF01')
            if owner:
                paper = get_paper(conference, kwargs['pk'], 'X2BF02')
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
            messages.warning(request, 'Permission Denied. Error Code: X2BF03')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2BF10')
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2BF11')
            if owner:
                paper = get_paper(conference, kwargs['pk'], 'X2BF12')
                form = PaperRecordForm(request.POST, request.FILES, instance=paper, sub=True)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Successfully Updated')
                    return redirect('conference:view_detail', slug=kwargs['slug'], pk=kwargs['pk'])
                else:
                    messages.error(request, 'Invalid Input. Try Again. Error Code: X2BF05')
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
            messages.warning(request, 'Permission Denied. Error Code: X2BF13')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2BF20')
            return redirect('home')


# noinspection PyBroadException
# Error Code X2BG01, X2BG02, X2BG03, X2BG10, X2BG11, X2BG12, X2BG13, X2BG20
class AddAuthor(TemplateView):
    template = 'view2/add_author.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2BG01')
            paper = get_paper(conference, kwargs['pk'], 'X2BG02')
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
            messages.warning(request, 'Permission Denied. Error Code: X2BG03')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2BG10')
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2BG11')
            paper = get_paper(conference, kwargs['pk'], 'X2BG04')
            if paper.user == request.user:
                form = AuthorRecordForm(request.POST, sub=conference.submission)
                if form.is_valid():
                    instance = form.save()
                    paper.author.add(instance)
                    messages.success(request, 'Successfully add Author')
                    return redirect('conference:view_detail', **kwargs)
                else:
                    messages.error(request, 'Invalid Input. Try Again. Error Code: X2BG12')
                form = AuthorRecordForm(sub=conference.submission)
                return render(request, self.template, {'slug': kwargs['slug'], 'pk': kwargs['pk'], 'form': form})
            else:
                raise PermissionDenied
        except ObjectDoesNotExist as msg:
            messages.error(request, msg)
            return redirect('home')
        except PermissionDenied:
            auth.logout(request)
            messages.warning(request, 'Permission Denied. Error Code: X2BG13')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2BG20')
            return redirect('home')


# noinspection PyBroadException
# Error Code X2BH01, X2BH02, X2BH03, X2BH04, X2BH10, X2BH11, X2BH12, X2BH13, X2BH14, X2BH15, X2BH20
class UpdateAuthor(TemplateView):
    template = 'view2/update_author.html'

    def get(self, request, *args, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2BH01')
            paper = get_paper(conference, kwargs['paper'], 'X2BH02')
            if paper.user == request.user or owner:
                author = get_author(kwargs['pk'], 'X2BH03')
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
            messages.warning(request, 'Permission Denied. Error Code: X2BH04')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2BH10')
            return redirect('home')

    def post(self, request, **kwargs):
        try:
            conference, owner = get_conference(request, kwargs['slug'], 'X2BH11')
            paper = get_paper(conference, kwargs['paper'], 'X2BH12')
            if paper.user == request.user or owner:
                author = get_author(kwargs['pk'], 'X2BH13')
                form = AuthorRecordForm(request.POST, instance=author, sub=conference.submission)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Successfully Updated')
                    return redirect('conference:view_detail', slug=kwargs['slug'], pk=kwargs['paper'])
                else:
                    messages.error(request, 'Invalid Input. Try Again. Error Code: X2BH14')
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
            messages.warning(request, 'Permission Denied. Error Code: X2BH15')
            return redirect('home')
        except Exception:
            auth.logout(request)
            messages.error(request, 'Error Code: X2BH20')
            return redirect('home')
