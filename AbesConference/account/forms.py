from django import forms
from django.contrib.auth import models, password_validation
from django.core.validators import validate_email


class SignupForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}), required=True, max_length=30)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}), required=True,
                                 max_length=20)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}), required=False,
                                max_length=30)
    email = forms.CharField(widget=forms.EmailInput(
        attrs={'placeholder': 'abcd@gmail.com', 'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,3}$'}), required=True,
        max_length=40)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), required=True,
                               max_length=20)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
                                       required=True, max_length=20)

    class Meta():
        model = models.User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def clean_username(self):
        user = self.cleaned_data['username']
        try:
            match = models.User.objects.get(username=user.lower())
        except:
            return user
        raise forms.ValidationError("Username already exits")

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            mt = validate_email(email)
        except:
            return forms.ValidationError("Email is not in correct format")
        try:
            match = models.User.objects.get(email=email.lower())
        except:
            return email
        raise forms.ValidationError("Email already exits")

    def clean_confirm_password(self):
        password1 = self.cleaned_data['password']
        password2 = self.cleaned_data['confirm_password']
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Password does not match")
            else:
                password_validation.validate_password(password2)


class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}), required=True,
                                 max_length=20)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}), required=False,
                                max_length=30)
    email = forms.CharField(widget=forms.EmailInput(
        attrs={'placeholder': 'abcd@gmail.com', 'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,3}$'}), required=True,
        max_length=40)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), required=True,
                               max_length=20)

    class Meta():
        model = models.User
        fields = ['email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            mt = validate_email(email)
        except:
            return forms.ValidationError("Email is not in correct format")
        return email


class ChangePasswordForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Current Password'}),
                                       required=True, max_length=20)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}), required=True,
                               max_length=20)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
                                       required=True, max_length=20)

    class Meta():
        model = models.User
        fields = ['password']

    def clean_confirm_password(self):
        password1 = self.cleaned_data['password']
        password2 = self.cleaned_data['confirm_password']
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Password does not match")
            else:
                password_validation.validate_password(password2)
