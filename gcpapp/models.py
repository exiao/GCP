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
    base_folder = models.ForeignKey("Folder",null=True)
    
    def delete(self, *args, **kwargs):
        self.base_folder.delete()
        super(UserProfile, self).delete(*args, **kwargs)
    
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
    
def content_file_name(instance, filename):
    return '/'.join([ instance.user.username,filename])
    
class Folder(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=50)
    parent = models.ForeignKey("Folder",related_name="folder_parent",null=True)
    sub_folders = models.ManyToManyField("Folder",related_name="sub")
    files = models.ManyToManyField("File")
    timestamp = models.DateTimeField(auto_now_add=True,null=True)
    def delete(self, *args, **kwargs):
        for file in self.files.all():
            file.delete()
        for folder in self.sub_folders.all():
            folder.delete()
        super(Folder, self).delete(*args, **kwargs)
    def __unicode__(self):
        return self.name
    
class File(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=50)
    file = models.FileField(upload_to=content_file_name)
    timestamp = models.DateTimeField(auto_now_add=True,null=True)
    def __unicode__(self):
        return self.name
    def delete(self, *args, **kwargs):
        self.file.delete()
        super(File, self).delete(*args, **kwargs)
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        folder = Folder.objects.create(user=instance,name='Base')
        finance = Folder.objects.create(user=instance,name='Finance',parent=folder)
        pictures = Folder.objects.create(user=instance,name='Pictures',parent=folder)
        miscellaneous = Folder.objects.create(user=instance,name='Miscellaneous',parent=folder) 
        folder.sub_folders.add(finance)
        folder.sub_folders.add(pictures)
        folder.sub_folders.add(miscellaneous)
        profile = UserProfile.objects.create(user=instance,base_folder=folder)
        
        
post_save.connect(create_user_profile, sender=User)
