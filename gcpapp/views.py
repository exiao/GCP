from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core import serializers
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from gcpapp.models import *
from django.core.context_processors import csrf
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail      
from settings import EMAIL_HOST_USER
from django.db.models import Max, Sum
import datetime


def home(request):   
    data={}
    images = Image.objects.filter(section="homepage_slideshow")
    data['images'] = images
    try:
        announcements = Announcement.objects.order_by('-pk')
        top = announcements.filter(entry__title = 'Top')[0]
        bottom_left = announcements.filter(entry__title = 'Bottom Left')[0]
        bottom_mid = announcements.filter(entry__title = 'Bottom Middle')[0]
        bottom_right = announcements.filter(entry__title = 'Bottom Right')[0]
        data['top'] = top
        data['bottom_left'] = bottom_left
        data['bottom_mid'] = bottom_mid
        data['bottom_right'] = bottom_right
        
        return render_to_response('home.html', data, context_instance=RequestContext(request))
    except:
        return render_to_response('home_orig.html',data, context_instance=RequestContext(request))
        
def green_groups(request):
    verified_users = User.objects.filter(is_staff=False,is_superuser=False,is_active=True)
    return render_to_response('green_groups.html', {'verified_users':verified_users},context_instance=RequestContext(request))
    
def about(request):
    return render_to_response('about.html', context_instance=RequestContext(request))
    
def resources(request):
    return render_to_response('resources.html', context_instance=RequestContext(request))
    
def reports(request):
    return render_to_response('reports.html', context_instance=RequestContext(request))
    
def contact(request):
    return render_to_response('contact.html', context_instance=RequestContext(request))
    
def signup(request):
    if request.method=="GET":
        form = UserForm()
        return render_to_response('signup.html',{'form':form}, context_instance=RequestContext(request))
    else:
        username = request.POST['username']
        group_name = request.POST['group_name']
        group_description = request.POST['group_description']
        email = request.POST['email']
        officer_name = request.POST['officer_name']
        academic_start_year = request.POST['academic_start_year']
        password = request.POST['password']
        
        try:
            user = User.objects.get(username=username)
            if user.is_active == False:
                user.delete()
                raise Exception
            title = "Sign Up Error"
            message = "That account exists already."
            return render_to_response('small_message.html', {'title': title,'message':message }, context_instance=RequestContext(request))
        except:
            pass
            
        try:
            user = User.objects.get(email=email)
            if user.is_active == False:
                user.delete()
                raise Exception
            title = "Sign Up Error"
            message = "That email is already being used."
            return render_to_response('small_message.html', {'title': title,'message':message }, context_instance=RequestContext(request))
        except:
            pass
        
        new_user = User()
        new_user.username = username
        new_user.email = email
        new_user.set_password(password)
        new_user.is_active = False
        new_user.save()
        
        user_profile = new_user.get_profile()
        user_profile.officer_name = officer_name
        user_profile.academic_start_year = academic_start_year
        user_profile.group_name = group_name
        user_profile.group_description = group_description
        user_profile.save()
        title = "Application Sent!"
        message = "Thank you for applying. You will receive an email whether or not your application was successful."
        return render_to_response('small_message.html',{'title':title,'message':message}, context_instance=RequestContext(request))

def login(request):
    if request.method == "GET":
        form = LoginForm()
        return render_to_response("login.html",{'form':form}, context_instance=RequestContext(request))
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                # Redirect to a success page.
                return HttpResponseRedirect('/')
            else:
                # Return a 'disabled account' error message
                title = "Login Fail"
                message = "Sorry, your application is still being processed. Please try some other time."
                return render_to_response('small_message.html',{'title':title,'message':message},context_instance=RequestContext(request))
        else:
            # Return an 'invalid login' error message.
            form = LoginForm(request.POST)
            return render_to_response("login.html",{'form':form,'fail':True}, context_instance=RequestContext(request))
            
def logout(request):
    auth_logout(request)
    title = "Logout Successful"
    message = "Success! You have logged out."
    return render_to_response('small_message.html',{'title':title,'message':message}, context_instance=RequestContext(request))
    
@login_required
def superuser(request):
    if request.user.is_superuser == False:
        return HttpResponseRedirect('/')
    return render_to_response('superuser/superuser_home.html', context_instance=RequestContext(request))
    
@login_required
def superuser_verify(request):
    data = {}
    if request.user.is_superuser == False:
        return HttpResponseRedirect('/')
    if request.method == "POST":
        for user_pk in request.POST:
            try: #if a non integer is passed skip it
                int(user_pk)
            except ValueError:
                continue
            action = request.POST[user_pk]
            user = User.objects.get(id=int(user_pk))
            if action == "verify":
                user.is_active = True
                user.get_profile().delete_me = False
                user.get_profile().save()
                #send_mail('ASUC Green Cat Application', "Congratulations, you're application has been approved. Your username is \"%s\" and you can now log in." % user.username, EMAIL_HOST_USER, [user.email])
                user.save()
            else:
                #send_mail('ASUC Green Cat Application', "Sorry, you're application was declined.", EMAIL_HOST_USER, [user.email])
                user.get_profile().delete()
                user.delete()
            data['message'] = "Actions successfully processed."
    
    non_verified_users = User.objects.filter(is_active=False)
    data['non_verified_users'] = non_verified_users

    delete_profiles = UserProfile.objects.filter(delete_me=True)
    data['delete_profiles'] = delete_profiles
    return render_to_response('superuser/superuser_verify.html',data, context_instance=RequestContext(request))

@login_required
def superuser_academic_year(request):
    data = {}
    if request.user.is_superuser == False:
        return HttpResponseRedirect('/')
    if request.method == "POST":

        if request.POST.__contains__("new_year"):
            new_year = request.POST["new_year"]
            try:
                AcademicYear.objects.get(year=new_year)
                data['message'] = "You can't add the year %d, because it already exists." % int(new_year)
            except:
                AcademicYear.objects.create(year=new_year)
                data['message'] = "The academic year %d has been added." % int(new_year)
        if request.POST.__contains__("delete_year"):
            delete_year_pk = request.POST["delete_year"]
            obj = AcademicYear.objects.get(id=delete_year_pk)
            year = obj.year
            obj.delete()
            data['message'] = "Year %d deleted" % year

    years = AcademicYear.objects.all().order_by('-year')
    data['years'] = years
    return render_to_response('superuser/superuser_academic_year.html',data, context_instance=RequestContext(request))

@login_required
def superuser_questions(request):
    if request.user.is_superuser == False:
        return HttpResponseRedirect('/')

    if request.method == "GET":
        data = {}
        question_groups = QuestionGroup.objects.all()
        data['question_groups'] = question_groups
        questions = QuestionBase.objects.all()
        data['questions'] = questions
        if request.GET.__contains__("message"):
            data['message'] = request.GET['message']
        return render_to_response('superuser/superuser_questions.html',data, context_instance=RequestContext(request))
    else:
        if request.POST.__contains__('delete_question_base'):
            question_base_id = request.POST['delete_question_base']
            QuestionBase.objects.get(id=question_base_id).delete()
            message = "Question deleted."
            return redirect('/superuser/questions/?message=%s' % message)

            
@login_required
def superuser_questions_edit(request):
    if request.user.is_superuser == False:
        return HttpResponseRedirect('/')
    if request.method == "GET":
        data = {}
        question_groups = QuestionGroup.objects.all()
        data['question_groups'] = question_groups
        return render_to_response('superuser/superuser_questions_edit.html',data, context_instance=RequestContext(request))
    else:
        if request.POST.__contains__('question_text'):
            question_text = request.POST['question_text']
            point_value = request.POST['point_value']
            question_group_id = request.POST['question_group_id']
            object,is_created = QuestionBase.objects.get_or_create(question_text=question_text, point_value=point_value)
            question_group = QuestionGroup.objects.get(id=int(question_group_id))
            question_group.question_bases.add(object)
            if is_created:
                message = "Question successfully created!"
            else:
                message = "That question and point value already exist."
            return redirect('/superuser/questions/?message=%s' % message)
        elif request.POST.__contains__('question_group'):
            question_group = request.POST['question_group']
            QuestionGroup.objects.create(title=question_group)
            message = "Question Group Created!"
            return redirect('/superuser/questions/?message=%s' % message)
        elif request.POST.__contains__('delete_question_group_id'):
            question_group_id = request.POST['delete_question_group_id']
            QuestionGroup.objects.get(id=int(question_group_id)).delete()
            message = "Question Group Deleted!"
            return redirect('/superuser/questions/?message=%s' % message)   
     
@login_required
def superuser_staff(request):
    data = {}
    if request.user.is_superuser == False:
        return HttpResponseRedirect('/')
    if request.method == "GET":
        if request.GET.__contains__('message'):
            data['message'] = request.GET['message']
            
        data['staff_members'] = User.objects.filter(is_staff=True,is_superuser=False)
        return render_to_response('superuser/superuser_staff.html',data, context_instance=RequestContext(request))
    
        
@login_required
def superuser_staff_user(request,user_id):
    data = {}
    if request.user.is_superuser == False:
        return HttpResponseRedirect('/')
        
    this_user = User.objects.get(id=user_id)
    profile = this_user.get_profile()
        
    if request.method == "GET":
        all_groups = User.objects.filter(is_staff=False,is_active=True)
        my_groups = profile.my_groups.all()
        data['all_groups'] = all_groups
        data['my_groups'] = my_groups
        data['this_user'] = this_user
        if request.GET.__contains__('message'):
            data['message'] = request.GET['message']
        return render_to_response('superuser/superuser_staff_user.html',data, context_instance=RequestContext(request))
    else:
        all_groups = User.objects.filter(is_staff=False,is_active=True)
        for group in all_groups:
            is_admin = request.POST[str(group.id)]
            if is_admin == "yes":
                profile.my_groups.add(group)
            else:
                profile.my_groups.remove(group)
        return redirect('/superuser/staff/%d/?message=Privileges Updated!' % this_user.id)
        
    
@login_required
def superuser_staff_create(request):
    data = {}
    if request.user.is_superuser == False:
        return HttpResponseRedirect('/')
    if request.method == "GET":
        return render_to_response('superuser/superuser_staff_create.html',data, context_instance=RequestContext(request))
    else:
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        account_type = request.POST['account_type']
        
        try:
            user = User.objects.get(username=username)
            if user.is_active == False:
                user.delete()
                raise Exception
            title = "Sign Up Error"
            message = "That username exists already."
            return render_to_response('small_message.html', {'title': title,'message':message }, context_instance=RequestContext(request))
        except:
            pass
        
        new_user = User()
        new_user.username = username
        new_user.email = email
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.set_password(password)
        new_user.is_staff = True
        if account_type == "superuser":
            new_user.is_superuser = True
        new_user.save()
        
        return redirect('/superuser/staff/?message=Staff member created!')

@login_required
def superuser_all_accounts(request):
    data = {}
    if request.user.is_superuser == False:
        return HttpResponseRedirect('/')
    if request.method == "GET":
        all_staff = User.objects.filter(is_active = True,is_staff=True).order_by('-is_superuser')
        all_groups = User.objects.filter(is_active = True,is_staff=False)
        data['all_staff'] = all_staff
        data['all_groups'] = all_groups
        return render_to_response('superuser/superuser_all_accounts.html',data,context_instance=RequestContext(request))
    else:
        delete_ids = request.POST.getlist('Delete')
        for id in delete_ids:
            user = User.objects.get(id=id)
            user.get_profile().delete()
            user.delete()
        return redirect('superuser_all_accounts')

@login_required
def superuser_finance(request):
    data = {}
    if request.user.is_superuser == False:
        return HttpResponseRedirect('/')
    if request.method == "GET":
        finance_requests = FinanceRequest.objects.filter(is_answered=False,admin_deleted=False)
        old_requests = FinanceRequest.objects.filter(is_answered=True,admin_deleted=False)
        data['finance_requests'] = finance_requests
        data['old_requests'] = old_requests
        return render_to_response('superuser/superuser_finance.html',data,context_instance=RequestContext(request))
    else:
        approved = request.POST.getlist('approve')
        declined = request.POST.getlist('decline')
        for finance_id in approved:
            finance = FinanceRequest.objects.get(id = int(finance_id))
            finance.is_approved = True
            finance.is_answered = True
            finance.save()
            #send_mail('ASUC Green Cat Finance Request', "You're finance request under the title: %s has been approved." % finance.title, EMAIL_HOST_USER, [finance.user.email])
        for finance_id in declined:
            finance = FinanceRequest.objects.get(id = int(finance_id))
            finance.is_approved = False
            finance.is_answered = True
            finance.save()
            #send_mail('ASUC Green Cat Finance Request', "You're finance request under the title: %s has been declined." % finance.title, EMAIL_HOST_USER, [finance.user.email])
        return redirect('superuser_finance')
        
@login_required
def superuser_finance_delete(request):
    if request.method == "POST":
        delete_list = request.POST.getlist("Delete")
        for delete_id in delete_list:
            finance_request = FinanceRequest.objects.get(id=int(delete_id))

            if finance_request.user_deleted:
                finance_request.delete()
            else:
                finance_request.admin_deleted = True
                finance_request.save()

        return redirect('superuser_finance')

@login_required
def superuser_content(request):
    data = {}
    if request.user.is_superuser == False:
        return HttpResponseRedirect('/')
        
    #top = Announcement.objects.get_or_create(entry__title='Top')
    #bot_left = Announcement.objects.get_or_create(entry__title='Bottom Left')
    #bot_mid = Announcement.objects.get_or_create(entry__title='Bottom Middle')
    #bot_right = Announcement.objects.get_or_create(entry__title='Bottom Right')
    #models = [top[0], bot_left[0], bot_mid[0], bot_right[0]]
    
    if request.method == 'POST':
        if request.POST.__contains__('delete_announcement'):
            announcement_id = request.POST['delete_announcement']
            Announcement.objects.get(pk=announcement_id).delete()
            return HttpResponseRedirect('.')
        elif request.POST.__contains__('photo_name'):
            photo_name = request.POST['photo_name']
            description = request.POST['description']
            image = request.FILES['image']
            obj = Image.objects.create(image=image,name=photo_name,description=description,section="homepage_slideshow")
            return redirect('/superuser/?message=%s' % "Image uploaded!")
        elif request.POST.__contains__('delete_image_id'):
            image_id = request.POST['delete_image_id']
            Image.objects.get(id=int(image_id)).delete()
            return redirect('/superuser/?message=%s' % "Image deleted!")
        

        formset = AnnouncementFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save()
        return HttpResponseRedirect('.')
    else:
        if request.GET.__contains__('message'):
            data['message'] = request.GET['message']
        
        formset = AnnouncementFormSet()
        for form in formset:
            print(form)
        data['forms'] = formset
        data['images'] = Image.objects.filter(section="homepage_slideshow")
        data.update(csrf(request))
        return render_to_response('superuser/superuser_content.html',data,context_instance=RequestContext(request))
        
@login_required
def staff(request):
    data = {}
    user = request.user
    profile = user.get_profile()
    if user.is_staff == False:
        return redirect('/')
    if request.method=="GET":
        if user.is_superuser:
            my_groups = User.objects.filter(is_staff=False,is_superuser=False)
        else:
            my_groups = profile.my_groups.all()
        data['my_groups'] = my_groups
        return render_to_response('staff/staff_my_groups.html',data,context_instance=RequestContext(request))

@login_required
def staff_group_files(request,group_id,folder_id):
    data = {}
    user = request.user
    profile = user.get_profile()
    if user.is_staff == False:
        return redirect('/')
    group = User.objects.get(id=group_id)
    return account_files(request,folder_id)
    
@login_required
def staff_checklist_redirect(request,group_id):
    data = {}
    max_year = AcademicYear.objects.all().aggregate(Max('year'))['year__max']
    if max_year is None:
        return render_to_response('small_message.html', {'title': 'Error','message':'Sorry, no active academic year exists. Please contact an administrator.' }, context_instance=RequestContext(request))
    return redirect('/staff/%d/checklist/%d' % ( int(group_id),max_year) )
    
@login_required
def staff_checklist(request,group_id,year):
    checklist_user = User.objects.get(id=group_id)
    return checklist_work(request,year,checklist_user)
        
#unused
@login_required
def account_settings(request):
    return render_to_response('account/account_settings.html', context_instance=RequestContext(request))
    
@login_required
def account_profile(request):
    data = {}
    if request.GET.__contains__('update'):
        data['update'] = request.GET['update']
    return render_to_response('account/account_profile.html', data, context_instance=RequestContext(request))
    
@login_required
def account_edit(request):
    readable_fields = {'group_name':'Group Name', 'password': 'Password','email':'Email','officer_name':'Officer Name',
        'academic_start_year':'Academic Start Year','group_description':'Group Description',
        'first_name':'First Name','last_name':'Last Name'}
    if request.method == "GET":
        field = request.GET['field']
        user = request.user
        profile = user.get_profile()
        data = {}
        data['field'] = str(field)
        read_field = readable_fields[field]
        data['read_field'] = read_field
        try: 
            # this one can't be done with vars for some reason
            exec('data_field = user.%s' %field)
        except AttributeError:
            profile_dict = vars(profile)
            data_field = profile_dict[field]
        data['data_field'] = data_field
        if request.GET.__contains__('old_field'):
            data['old_field'] = request.GET['old_field']
        return render_to_response('account/account_edit.html',data, context_instance=RequestContext(request))
    else:
        field = request.POST['field']
        new_field = request.POST[field]
        username = request.user.username
        password = request.POST['check_password']
        user = authenticate(username=username, password=password)
        if user is None:
            return HttpResponseRedirect('/account/profile/edit?field=%s&old_field=%s' % (field,new_field))
        profile = user.get_profile()
        
        if field=="password":
            user.set_password(new_field)
            user.save()
        else:
            try: 
                user_dict = vars(user)
                user_dict[field] #this will throw an error if the field doesn't exist
                user_dict[field] = new_field
                user.save()
            except KeyError:
                profile_dict = vars(profile)
                profile_dict[field]
                profile_dict[field] = new_field
                profile.save()
        return HttpResponseRedirect('/account/profile/?update=%s' % readable_fields[field])
        
@login_required
def account_files(request,folder_id):
    data = {}
    folder = Folder.objects.get(id=folder_id)
    if request.user != folder.user and request.user.is_staff == False:
        return redirect('/account/profile')
    #this happens on file upload
    if request.method == "POST" and request.FILES.__contains__('file'):
        file = request.FILES['file']
        obj = File.objects.create(file=file,name=str(file),user=folder.user)
        profile = folder.user.get_profile()
        folder.files.add(obj)
        message = 'File uploaded!'
        return redirect('/account/files/%d' % int(folder_id))#%d?message=%s' % (int(folder_id),message))
        
    #this happens on folder creation
    elif request.method == "POST" and request.POST.__contains__('folder'):
        folder_name = request.POST['folder']
        new_folder = Folder.objects.create(name=folder_name,user=folder.user,parent=folder)
        folder.sub_folders.add(new_folder)
        folder.save()
        message = 'Folder created!'
        return redirect('/account/files/%d' % int(folder_id)) #%d?message=%s' % (int(folder_id),message))
        
    else:
        if request.GET.__contains__('message'):
            data['message'] = request.GET['message']
        folders = folder.sub_folders.all().order_by('-timestamp')
        files = folder.files.all().order_by('-timestamp')
        
        node = folder
        tree = []
        while node is not None:
            tree.append(node)
            node = node.parent
        tree.reverse()
        
        #crop out the last element to apply special properties in the front end
        if len(tree) > 1:
            most = tree[0:len(tree)-1]
            data['most'] = most
            last = tree[len(tree)-1]
            data['last']=last
        else:
            data['last'] = tree[0]

        data['folders'] = folders
        data['files'] = files
        data['folder_owner'] = folder.user
        return render_to_response('account/account_files.html',data, context_instance=RequestContext(request))
        
@login_required
def account_delete(request):
    data = {}
    if request.method=="GET":
        if request.GET.__contains__('wrong'):
            data['wrong'] = True
        return render_to_response('account/account_delete.html',data,context_instance=RequestContext(request))
    else:
        password = request.POST['password']
        user = authenticate(username=request.user.username, password=password)
        if user is None:
            return redirect("/account/profile/delete?wrong=password")
        else:
            auth_logout(request)
            profile = user.get_profile()
            profile.delete_me = True
            profile.save()
            #profile.delete()
            #user.delete()
            message = 'Your request to delete your account has been sent.'
            return render_to_response('small_message.html',{'title':'Delete Request Sent','message':message}, context_instance=RequestContext(request))

@login_required
def account_checklist_redirect(request):
    data = {}
    max_year = AcademicYear.objects.all().aggregate(Max('year'))['year__max']
    if max_year is None:
        return render_to_response('small_message.html', {'title': 'Error','message':'Sorry, no active academic year exists. Please contact an administrator.' }, context_instance=RequestContext(request))
    return redirect('/account/checklist/%d' % max_year)

@login_required
def account_checklist(request,year):
    return checklist_work(request,year,request.user)
    
#this exists because 2 things will refer to the same view (account_checklist and staff_checklist)
def checklist_work(request,year,checklist_user):
    data = {}
    data['year'] = year
    academic_year = AcademicYear.objects.get(year=year)
    if request.method == "GET":
        if request.GET.__contains__('message'):
            data['message'] = request.GET['message']
        checklist, created = Checklist.objects.get_or_create(user=checklist_user, academic_year=academic_year)

        for question_base in QuestionBase.objects.all():
            if not checklist.questions.filter(question_base=question_base).exists():
                question,created = Question.objects.get_or_create(user=checklist_user,
                    question_base = question_base,
                    question_text = question_base.question_text,
                    point_value = question_base.point_value,
                    academic_year = academic_year)
                checklist.questions.add(question)

        questions = checklist.questions.all()
        data['question_groups'] = QuestionGroup.objects.all()
        data['questions'] = questions
        data['checklist'] = checklist
        data['all_years'] = AcademicYear.objects.all().order_by('year')
        data['checklist_user'] = checklist.user
        
        data['curr_points'] = Question.objects.filter(user=checklist_user,academic_year=academic_year,is_approved=True).aggregate(Sum('point_value'))['point_value__sum']
        data['max_points'] = Question.objects.filter(user=checklist_user,academic_year=academic_year).aggregate(Sum('point_value'))['point_value__sum']
        
        if data['curr_points'] is None:
            data['curr_points'] = 0
        return render_to_response('account/account_checklist.html',data,context_instance=RequestContext(request))
    else:
        checklist = Checklist.objects.get(user=checklist_user, academic_year=academic_year)
        for question in checklist.questions.all():
            description_key = str(question.id) + "_description"
            if request.POST.__contains__(description_key):
                description = request.POST[description_key]
                question.description = description
            
            approved_key = str(question.id)+"_is_approved"
            if request.POST.__contains__(approved_key):
                is_approved = request.POST[approved_key]
                if is_approved == "yes":
                    question.is_approved = True
                else:
                    question.is_approved = False
                    
            admin_comment_key = str(question.id)+"_admin_comment"
            if request.POST.__contains__(admin_comment_key):
                admin_comment = request.POST[admin_comment_key]
                question.admin_comment = admin_comment

            files_key = str(question.id) + "_file"
            files_list = request.FILES.getlist(files_key)

            for file in files_list:
                obj = File.objects.create(file=file,name=str(file),user=checklist_user)
                question.files.add(obj)

            question.save()

        for file_id in request.POST.getlist("file_delete"):
            File.objects.get(id=file_id).delete()
        
        if request.user.is_staff:
            return redirect('/staff/%d/checklist/%d/?message=Checklist updated!' % ( int(checklist_user.id), int(year)) )
        else:
            checklist.timestamp = datetime.datetime.now()
            checklist.save()
            return redirect('/account/checklist/%d/?message=Checklist updated!' % int(year))

@login_required
def account_finance_request(request):
    data = {}
    if request.method == "GET":
        my_finance_requests = FinanceRequest.objects.filter(user=request.user,user_deleted=False).order_by('-timestamp')
        data['my_finance_requests'] = my_finance_requests
        if request.GET.__contains__('message'):
            data['message'] = request.GET['message']
        return render_to_response('account/account_finance_request.html',data,context_instance=RequestContext(request))
    else:
        delete_list = request.POST.getlist("Delete")
        for delete_id in delete_list:
            finance_request = FinanceRequest.objects.get(id=int(delete_id))
            if finance_request.is_answered:
                if finance_request.admin_deleted:
                    finance_request.delete()
                else:
                    finance_request.user_deleted = True
                    finance_request.save()
            else:
                finance_request.delete()
        return redirect(".")
            
@login_required
def account_finance_request_create(request):
    data = {}
    if request.method == "GET":
        form = FinanceRequestForm()
        data['form'] = form
        return render_to_response('account/account_finance_request_create.html',data,context_instance=RequestContext(request))
    else:
        form = FinanceRequestForm(request.POST)
        if form.is_valid():
            # SEND MAIL?
            fin = form.save(commit=False)
            fin.user = request.user
            fin.save()
            message = 'Your finance request has been sent. You will be notified through email with the response.'
            return redirect('/account/finance_request/?message=%s' % message)
        else: #this shouldn't run as the front end will validate the form
            data['form'] = form
            return render_to_response('account/account_finance_request_create.html',data,context_instance=RequestContext(request))      

@login_required
def ajax_delete_folder(request):
    if request.method == "POST" and request.is_ajax():
        folder_id = request.POST['folder_id']
        folder = Folder.objects.get(id=folder_id)
        folder.delete()
        return HttpResponse("success")
        
@login_required
def ajax_delete_file(request):
    if request.method == "POST" and request.is_ajax():
        file_id = request.POST['file_id']
        file = File.objects.get(id=file_id)
        file.delete()
        return HttpResponse("success")