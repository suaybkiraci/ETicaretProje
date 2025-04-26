from django import forms
from django.contrib.auth.models import User

class ProductForm(forms.Form):
    name = forms.CharField(max_length=200)
    price = forms.FloatField()
    description = forms.CharField(widget=forms.Textarea)
    image = forms.ImageField()

class ProfileForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','email']

        
