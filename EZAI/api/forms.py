from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from markdownx.fields import MarkdownxFormField
from .models import ModelDocumentation, MLModel

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required')
    email = forms.EmailField(max_length=254, required=True,
                             help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

class ChangeEmail(forms.Form):
    email1 = forms.EmailField(label=u'Type new Email')
    email2 = forms.EmailField(label=u'Type new Email again')

class CreateModelForm(forms.Form):
    title = forms.CharField(required=True, label='Enter the Title of the model')
    description = forms.CharField(required=True, label='Enter a description of the model')
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )

# Can you edit anyones form while its just hiddeninput? 
class DocsEditor(forms.ModelForm):
    id = forms.IntegerField(widget = forms.HiddenInput(), required=True)
    mlmodel = forms.ModelChoiceField(queryset=MLModel.objects.all(), widget=forms.HiddenInput(), required=False)
    documentation = MarkdownxFormField()

    class Meta: 
        model = ModelDocumentation
        fields = ('id', 'mlmodel', 'documentation')
        
class CreateClientForm(forms.Form):
    client_name = forms.CharField(max_length=30, required=True, label='Client Name')
    ml_model = forms.ModelChoiceField(queryset=MLModel.objects.exclude(reviewed=False), to_field_name="title")

class ManageUsersForm(forms.Form):
    key = forms.CharField(max_length=500, widget=forms.HiddenInput())
    
