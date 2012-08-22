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

def home(request):
    return render_to_response('home.html', context_instance=RequestContext(request))
    
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
            return render_to_response('signup_response.html', {'fail': True }, context_instance=RequestContext(request))
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
        return render_to_response('signup_response.html', context_instance=RequestContext(request))

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
                return render_to_response('login_inactive.html',context_instance=RequestContext(request))
        else:
            # Return an 'invalid login' error message.
            form = LoginForm(request.POST)
            return render_to_response("login.html",{'form':form,'fail':True}, context_instance=RequestContext(request))
            
def logout(request):
    auth_logout(request)
    return render_to_response('logout_success.html')