from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.db.models.signals import post_save
from django.forms import ModelForm
from django.forms.models import modelformset_factory

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    group_name = models.CharField(max_length=70,null=True)
    officer_name = models.CharField(max_length=50,null=True)
    academic_start_year = models.IntegerField(null=True)
    base_folder = models.ForeignKey("Folder",null=True)
    delete_me = models.BooleanField(default=False)
    group_description = models.TextField()

    #if user is an admin
    my_groups = models.ManyToManyField(User,related_name="my_groups_set")

    def delete(self, *args, **kwargs):
        self.base_folder.delete()
        super(UserProfile, self).delete(*args, **kwargs)

class UserForm(forms.Form):
    username = forms.CharField(max_length=30)
    group_name = forms.CharField(max_length=70)
    group_description = forms.CharField(widget=forms.Textarea)
    email = forms.EmailField()
    officer_name = forms.CharField(max_length=50, label="Sustainability Officer Name")
    academic_start_year = forms.IntegerField()
    password = forms.CharField(widget=forms.PasswordInput , label="Password")
    password_again = forms.CharField( widget=forms.PasswordInput, label="Password (again)" )

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput , label="Password")

def content_file_name(instance, filename):
    return '/'.join(['users', instance.user.username,filename])

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

class Image(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True,blank=True)
    section = models.CharField(max_length=50,null=True)
    image = models.ImageField(upload_to="images")
    timestamp = models.DateTimeField(auto_now_add=True,null=True)
    def __unicode__(self):
        return self.name
    def delete(self, *args, **kwargs):
        self.image.delete()
        super(Image, self).delete(*args, **kwargs)

class AcademicYear(models.Model):
    year = models.IntegerField(unique=True)
    def __unicode__(self):
        return str(self.year)

class QuestionBase(models.Model):
    question_text = models.TextField()
    point_value = models.IntegerField()
    
    def delete(self, *args, **kwargs):
        for question in self.question_base.all():
            question.delete()
        super(QuestionBase, self).delete(*args, **kwargs)
    def __unicode__(self):
        return self.question_text

class Question(models.Model):
    #AcademicYear.objects.filter(year=2012).aggregate(Sum('year'))
    user = models.ForeignKey(User)
    admin_comment = models.TextField(default="",blank=True)
    question_base = models.ForeignKey(QuestionBase,related_name="question_base")
    academic_year = models.ForeignKey(AcademicYear)
    question_text = models.TextField(null=True)
    description = models.TextField(default="",blank=True)
    files = models.ManyToManyField("File")
    is_approved = models.BooleanField(default=False)
    point_value = models.IntegerField(null=True)
    def delete(self, *args, **kwargs):
        for file in self.files.all():
            file.delete()
        super(Question, self).delete(*args, **kwargs)
    def __unicode__(self):
        return self.question_base.question_text

class QuestionGroup(models.Model):
    title = models.CharField(max_length=100)
    question_bases = models.ManyToManyField("QuestionBase")
    def delete(self, *args, **kwargs):
        for question in self.question_bases.all():
            question.delete()
        super(QuestionGroup, self).delete(*args, **kwargs)
    def __unicode__(self):
        return self.title
        
class Checklist(models.Model):
    user = models.ForeignKey(User)
    questions = models.ManyToManyField("Question")
    academic_year = models.ForeignKey("AcademicYear")
    timestamp = models.DateTimeField(auto_now_add=True,null=True)
    def __unicode__(self):
        return str(self.user) + "-" + str(self.academic_year.year)

class Announcement(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)
    body = models.TextField(default="", blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True,null=True)
    #images = models.ManyToManyField("Image")
    entry = models.CharField(max_length=50)
    def __unicode__(self):
        return self.title

class AnnouncementForm(ModelForm):
    class Meta:
        model = Announcement
        exclude = ('entry','timestamp')

AnnouncementFormSet = modelformset_factory(Announcement, max_num=0, exclude=('entry',))

class FinanceRequest(models.Model):
    user = models.ForeignKey(User)
    description = models.TextField(default="",blank=True)
    reimburse_name = models.CharField(max_length=40)
    student_id_or_group_num = models.CharField(max_length=40)
    address = models.TextField(default="",blank=True)
    is_approved = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    receipt_file = models.OneToOneField("File",null=True)
    timestamp = models.DateTimeField(auto_now_add=True,null=True)
    is_answered = models.BooleanField(default=False) #whether or not an admin responded
    admin_deleted = models.BooleanField(default=False)
    user_deleted = models.BooleanField(default=False)
    
    def delete(self, *args, **kwargs):
        self.receipt_file.delete()
        super(FinanceRequest, self).delete(*args, **kwargs)
    def __unicode__(self):
        return str(self.user.username) + " - $%d" % self.amount

class FinanceRequestForm(ModelForm):
    description = forms.CharField(label="Which point will this help you complete?",widget=forms.Textarea)
    reimburse_name = forms.CharField(label="Who should we reimburse?")
    student_id_or_group_num = forms.CharField(label="Student ID or Group Account #")
    address = forms.CharField(label="Address (if student group, please use ASUC Address)",widget=forms.Textarea)
    class Meta:
        model = FinanceRequest
        exclude = ('user','is_approved','is_answered','admin_deleted','user_deleted','receipt_file') #implicit fields
        fields = ('amount','description','reimburse_name','student_id_or_group_num','address') #specifies order


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        folder = Folder.objects.create(user=instance,name='Base')
        finance = Folder.objects.create(user=instance,name='Finance',parent=folder)
        pictures = Folder.objects.create(user=instance,name='Pictures',parent=folder)
        miscellaneous = Folder.objects.create(user=instance,name='Miscellaneous',parent=folder)
        reports = Folder.objects.create(user=instance,name='Reports',parent=folder)
        folder.sub_folders.add(finance)
        folder.sub_folders.add(pictures)
        folder.sub_folders.add(miscellaneous)
        folder.sub_folders.add(reports)
        profile = UserProfile.objects.create(user=instance,base_folder=folder)
        if instance.is_superuser:
            for user in User.objects.filter(is_staff=False):
                profile.my_groups.add(user)


post_save.connect(create_user_profile, sender=User)
