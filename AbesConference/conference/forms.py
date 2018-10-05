from django import forms

from .models import PaperRecord, AuthorRecord, ReviewPaperRecord, ConferenceRecord


class ConferenceForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Conference Name'}), required=True, max_length=140)
    slug = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Acronym', 'pattern': "[^'\x22]+"}), required=True,
        max_length=30)
    description = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Conference Detail'}), required=True, max_length=1000)
    end_date = forms.DateField(widget=forms.widgets.DateInput(
        attrs={'class': 'form-control', 'placeholder': 'yyyy-mm-dd', 'style': "width: 150px"}, format="%Y/%m/%d"),
        required=True, )

    class Meta:
        model = ConferenceRecord
        fields = ['slug', 'name', 'description', 'end_date']


class AuthorRecordForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Full Name*'}), max_length=50, required=True)
    email = forms.CharField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email*', 'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,3}$'}),
        max_length=50, required=True)
    mobileNumber = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Mobile Number*', 'pattern': "[789][0-9]{9}"}),
        max_length=10, required=True)
    country = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Country Name*'}), max_length=50, required=True)
    organization = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Organization*'}), max_length=100, required=True)
    url = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'http://example.com/', 'pattern': "https?://.+"}),
        max_length=50, required=False)

    class Meta:
        model = AuthorRecord
        fields = ['name', 'email', 'mobileNumber', 'country', 'organization', 'url']

    def __init__(self, *args, sub, **kwargs):
        super(AuthorRecordForm, self).__init__(*args, **kwargs)
        if not sub:
            self.fields['name'].widget.attrs['disabled'] = True
            self.fields['email'].widget.attrs['disabled'] = True
            self.fields['mobileNumber'].widget.attrs['disabled'] = True
            self.fields['country'].widget.attrs['disabled'] = True
            self.fields['organization'].widget.attrs['disabled'] = True
            self.fields['url'].widget.attrs['disabled'] = True


class AuthorRecordForm1(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Full Name'}), max_length=50, required=False)
    email = forms.CharField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email', 'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,3}$'}),
        max_length=50, required=False)
    mobileNumber = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Mobile Number', 'pattern': "[789][0-9]{9}"}),
        max_length=10, required=False)
    country = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Country Name'}), max_length=50, required=False)
    organization = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Organization'}), max_length=100, required=False)
    url = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'http://example.com/', 'pattern': "https?://.+"}),
        max_length=50, required=False)

    class Meta:
        model = AuthorRecord
        fields = ['name', 'email', 'mobileNumber', 'country', 'organization', 'url']

    def __init__(self, *args, sub, **kwargs):
        super(AuthorRecordForm1, self).__init__(*args, **kwargs)
        if not sub:
            self.fields['name'].widget.attrs['disabled'] = True
            self.fields['email'].widget.attrs['disabled'] = True
            self.fields['mobileNumber'].widget.attrs['disabled'] = True
            self.fields['country'].widget.attrs['disabled'] = True
            self.fields['organization'].widget.attrs['disabled'] = True
            self.fields['url'].widget.attrs['disabled'] = True


class PaperRecordForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title*'}),
                            required=True, max_length=200)
    abstract = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Abstract*'}),
                               required=True, max_length=2000)
    keywords = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Keywords*'}),
                               required=True, max_length=200)
    file = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'class': 'custom-file-input', 'style': "opacity:1", 'accept': '.pdf'}), required=True)

    class Meta:
        model = PaperRecord
        fields = ['title', 'abstract', 'keywords', 'file']

    def __init__(self, *args, sub, **kwargs):
        super(PaperRecordForm, self).__init__(*args, **kwargs)
        if not sub:
            self.fields['title'].widget.attrs['disabled'] = True
            self.fields['abstract'].widget.attrs['disabled'] = True
            self.fields['keywords'].widget.attrs['disabled'] = True
            self.fields['file'].widget.attrs['disabled'] = True


class ConfirmationForm(forms.Form):
    confirmation = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-3'}), max_length=15,
                                   required=True)


class ReviewPaperForm(forms.ModelForm):
    overallEvaluation = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Your comment'}), max_length=500)
    point = forms.CharField(widget=forms.NumberInput(), max_length=5)
    remark = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Remark'}), max_length=100)

    class Meta:
        model = ReviewPaperRecord
        fields = ['overallEvaluation', 'point', 'remark']


class EmailForm(forms.Form):
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)


class EmailToAuthorsForm(forms.Form):
    subject = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Subject', 'class': 'form-control col-md-7'}), required=True)
    message = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'Message', 'class': 'form-control col-md-7'}), required=True)


class AddPcMemberForm(forms.Form):
    emails = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'FirstName,LastName,example@abc.com', 'class': 'form-control col-md-7'}), required=True)
    message = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'Message', 'class': 'form-control col-md-7'}), required=False)
    file = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'class': 'custom-file-input', 'accept': '.pdf'}), required=False)
