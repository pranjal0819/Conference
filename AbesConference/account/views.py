from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages, auth
from .forms import SignupForm, EditProfileForm, ChangePasswordForm


# Create your views here.
class Login(TemplateView):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        username = request.POST['user']
        password = request.POST['pass']
        if username is not "":
            try:
                auth.models.User.objects.get(username=username.lower())
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
        return render(request, self.template_name, {})


class Signup(TemplateView):
    template_name = 'signup.html'

    def get(self, request):
        form = SignupForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            firstName = form.cleaned_data['first_name']
            lastName = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            auth.models.User.objects.create_user(username=username.lower(), first_name=firstName, last_name=lastName,
                                                 email=email.lower(), password=password)

            messages.success(request, 'user registration successfully.')
            return redirect("account:signup")
        else:
            messages.error(request, "Please try again")
        return render(request, self.template_name, {'form': form})


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
            match = auth.models.User.objects.filter(email=email.lower())
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
