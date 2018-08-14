from django import forms

from .models import PaperRecord, AuthorRecord, ReviewPaperRecord, ConferenceRecord


class ConferenceForm(forms.ModelForm):
    slug = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Conference Name', 'pattern': "[^'\x22]+", 'style': "width: 350px"}), max_length=30)
    description = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'Conference Detail', 'style': "width:350px; height:150px"}), max_length=100)
    start_date = forms.DateField(widget=forms.widgets.DateInput(
        attrs={'placeholder': 'yyyy-mm-dd', 'style': "width: 150px"}, format="%Y/%m/%d"))
    end_date = forms.DateField(widget=forms.widgets.DateInput(
        attrs={'placeholder': 'yyyy-mm-dd', 'style': "width: 150px"}, format="%Y/%m/%d"))

    class Meta:
        model = ConferenceRecord
        fields = ['slug', 'description', 'start_date', 'end_date']


class AuthorRecordForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Name'}), max_length=50)
    email = forms.CharField(widget=forms.EmailInput(
        attrs={'placeholder': 'abcd@gmail.com', 'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,3}$'}), max_length=50)
    mobileNumber = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Mobile Number', 'pattern': "[789][0-9]{9}"}), max_length=10)
    country = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Country Name'}), max_length=50)
    organization = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Organization'}), max_length=100)
    url = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'http://example.com/', 'pattern': "https?://.+"}), required=False, max_length=50)

    class Meta:
        model = AuthorRecord
        fields = ['name', 'email', 'mobileNumber', 'country', 'organization', 'url']


class PaperRecordForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Title*'}), required=True, max_length=200)
    abstract = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Abstract*'}), required=True,
                               max_length=1000)
    keywords = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Keywords*'}), required=True, max_length=200)
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'accept': '.pdf,.doc', 'style': "border:none"}),
                           required=True)

    class Meta:
        model = PaperRecord
        fields = ['title', 'abstract', 'keywords', 'file']


class ReviewPaperForm(forms.ModelForm):
    overallEvaluation = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Your comment'}), max_length=500)
    point = forms.CharField(widget=forms.NumberInput(), max_length=5)
    remark = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Remark'}), max_length=100)

    class Meta:
        model = ReviewPaperRecord
        fields = ['overallEvaluation', 'point', 'remark']
