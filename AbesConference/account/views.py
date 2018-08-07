import json
import urllib
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages, auth
from django.core.mail import EmailMessage

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

from django.contrib.auth.models import User
from django.conf import settings
from .forms import SignupForm, EditProfileForm, ChangePasswordForm
from .tokens import account_activation_token



def logout(request):
    auth.logout(request)
    return redirect("home")

class Profile(TemplateView):
    template_name = 'profile.html'

    def get(self, request):
        return render(request, self.template_name, {})

class EditProfile(TemplateView):
    template_name = 'editProfile.html'

    def get(self, request):
        form = EditProfileForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = EditProfileForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            match = User.objects.filter(email=email.lower())
            if request.user.email == email or not match:
                user = auth.authenticate(username=request.user, password=password)
                if user is not None:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.email = email
                    user.save(update_fields=['first_name', 'last_name', 'email'])
                    messages.success(request, "Successfully profile updated")
                else:
                    messages.error(request, "Password doesn't match")
            else:
                messages.error(request, "Email already taken")
        else:
            messages.error(request, "Please try again")
        return render(request, self.template_name, {'form': form})


class ChangeUsername(TemplateView):
    template_name = 'profile.html'

    def get(self, request):
        return render(request, self.template_name, {})


class ChangePassword(TemplateView):
    template_name = 'profile.html'

    def get(self, request):
        return render(request, self.template_name, {})


class Login(TemplateView):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        try:    
            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.RECAPTCHA_PRIVATE_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req =  urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            ''' End reCAPTCHA validation '''
            if result['success']:
                username = request.POST['user']
                password = request.POST['pass']
                if username is not "":
                    try:
                        User.objects.get(username=username.lower())
                        user = auth.authenticate(username=username.lower(), password=password)
                        if user is not None:
                            auth.login(request, user)
                            if 'next' in request.POST:
                                return redirect(request.POST.get('next'))
                            return redirect("conference:welcome")
                        else:
                            messages.error(request, "Username and password did not match")
                    except:
                        messages.error(request, "User does not exit")
                else:
                    messages.error(request, "Enter Username and Password")
            else:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
        except:
            return redirect("account:login")
        return render(request, self.template_name, {})


class Signup(TemplateView):
    template_name = 'signup.html'

    def get(self, request):
        form = SignupForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                ''' Begin reCAPTCHA validation '''
                recaptcha_response = request.POST.get('g-recaptcha-response')
                url = 'https://www.google.com/recaptcha/api/siteverify'
                values = {
                    'secret': settings.RECAPTCHA_PRIVATE_KEY,
                    'response': recaptcha_response
                }
                data = urllib.parse.urlencode(values).encode()
                req =  urllib.request.Request(url, data=data)
                response = urllib.request.urlopen(req)
                result = json.loads(response.read().decode())
                ''' End reCAPTCHA validation '''
                if result['success']:
                    username = form.cleaned_data['username']
                    firstName = form.cleaned_data['first_name']
                    lastName = form.cleaned_data['last_name']
                    email = form.cleaned_data['email']
                    password = form.cleaned_data['password']

                    user = User.objects.create_user(username=username.lower(), first_name=firstName,
                                                     last_name=lastName, email=email.lower(), password=password, is_active=False)
                    print(user.pk)
                    '''Begin Email Sending '''
                    current_site = get_current_site(request)
                    mail_subject = 'Activate your Conference Account.'
                    message = render_to_string('acc_active_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                        'token':account_activation_token.make_token(user),
                    })
                    email = EmailMessage(mail_subject, message, to=[user.email])
                    email.send()
                    '''End Email sending'''
                    messages.success(request, 'Please confirm your email address to complete the registration.')
                    return redirect("account:login")
                else:
                    messages.error(request, "Invalid reCAPTCHA. Please try again.")
            except:
                return redirect("account:signup")
        else:
            messages.error(request, "Please try again")
        return render(request, self.template_name, {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        auth.login(request, user)
        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect("account:login")
    else:
        messages.error(request,'Activation link is invalid!')
        return redirect("account:signup")
