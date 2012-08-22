from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.db.models.signals import post_save

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    group_name = models.CharField(max_length=70,null=True)
    officer_name = models.CharField(max_length=50,null=True)
    academic_start_year = models.IntegerField(null=True)
    
class UserForm(forms.Form):
    username = forms.CharField(max_length=30)
    group_name = forms.CharField(max_length=70)
    email = forms.EmailField()
    officer_name = forms.CharField(max_length=50, label="Sustainability Officer Name")
    academic_start_year = forms.IntegerField()
    password = forms.CharField(widget=forms.PasswordInput , label="Password")
    password_again = forms.CharField( widget=forms.PasswordInput, label="Password (again)" )
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput , label="Password")
    

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
