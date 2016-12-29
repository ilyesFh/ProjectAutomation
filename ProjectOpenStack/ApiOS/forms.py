from django import forms

class SingUpForm(forms.Form):
    name=forms.CharField(250,widget=forms.TextInput(attrs={'placeholder': 'name '}))
    tenant=forms.CharField(250,widget=forms.TextInput(attrs={'placeholder': 'tenant '}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'password '}))
