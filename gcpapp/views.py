from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core import serializers
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from gcpapp.models import *
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail      
from settings import EMAIL_HOST_USER

def home(request):
    return render_to_response('home.html', context_instance=RequestContext(request))
    
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
        user_profile.save()
        title = "Application Sent!"
        message = "Thank you for applying. You will receive an email whether or not your application was successful."
        return render_to_response('signup_response.html',{'title':title,'message':message}, context_instance=RequestContext(request))

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
                #send_mail('ASUC Green Cat Application', "Congratulations, you're application has been approved. Your username is \"%s\" and you can now log in." % user.username, EMAIL_HOST_USER, [user.email])
                user.save()
            else:
                #send_mail('ASUC Green Cat Application', "Sorry, you're application was declined.", EMAIL_HOST_USER, [user.email])
                user.delete()
            data['message'] = "Actions successfully processed."
    
    non_verified_users = User.objects.filter(is_active=False)
    data['non_verified_users'] = non_verified_users
    return render_to_response('superuser/superuser_verify.html',data, context_instance=RequestContext(request))

    
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
    readable_fields = {'group_name':'Group Name', 'password': 'Password','email':'Email','officer_name':'Officer Name','academic_start_year':'Academic Start Year'}
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