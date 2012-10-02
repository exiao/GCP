from django.conf.urls import patterns, include, url
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('gcpapp.views',

    url(r'^$', 'home', name='home'),
    url(r'^about/$', 'about', name='about'),
    url(r'^green_groups/$', 'green_groups', name='green_groups'),
    url(r'^resources/$', 'resources', name='resources'),
    url(r'^reports/$', 'reports', name='reports'),
    url(r'^contact/$', 'contact', name='contact'),
    url(r'^signup/$', 'signup', name='signup'),
    url(r'^accounts/login/$', 'login', name='login'),
    url(r'^logout/$', 'logout', name='logout'),
    
    #SUPERUSER SECTION
    url(r'^superuser/$', 'superuser_content', name='superuser'),
    url(r'^superuser/verify/$', 'superuser_verify', name='superuser_verify'),
    url(r'^superuser/academic_year/$', 'superuser_academic_year', name='superuser_academic_year'),
    url(r'^superuser/questions/$', 'superuser_questions', name='superuser_questions'),
    url(r'^superuser/staff/$', 'superuser_staff', name='superuser_staff'),
    url(r'^superuser/staff/(?P<user_id>\d+)/$', 'superuser_staff_user', name='superuser_staff_user'),
    url(r'^superuser/staff/create/$', 'superuser_staff_create', name='superuser_staff_create'),
    url(r'^superuser/all_accounts/$', 'superuser_all_accounts', name='superuser_all_accounts'),
    url(r'^superuser/finance/$', 'superuser_finance', name='superuser_finance'),
    url(r'^superuser/finance/delete$', 'superuser_finance_delete', name='superuser_finance_delete'),
    
    #STAFF SECTION
    url(r'^staff/$', 'staff', name='staff'),
    url(r'^staff/(?P<group_id>\d+)/files/(?P<folder_id>\d+)/$', 'staff_group_files', name='staff_group_files'), 
    url(r'^staff/(?P<group_id>\d+)/checklist/$', 'staff_checklist_redirect', name='staff_checklist_redirect'),
    url(r'^staff/(?P<group_id>\d+)/checklist/(?P<year>\d+)/$', 'staff_checklist'),
    
    #ACCOUNT SECTION
    url(r'^account/profile/$', 'account_profile', name='account_profile'),
    url(r'^account/profile/edit/$', 'account_edit', name='account_edit'),
    url(r'^account/profile/delete/$', 'account_delete', name='account_delete'),
    url(r'^account/settings/$', 'account_settings', name='account_settings'),
    url(r'^account/files/(?P<folder_id>\d+)/$', 'account_files'),
    url(r'^account/checklist/$', 'account_checklist_redirect', name='account_checklist_redirect'),
    url(r'^account/checklist/(?P<year>\d+)/$', 'account_checklist'),
    url(r'^account/finance_request/$', 'account_finance_request',name="account_finance_request"),
    url(r'^account/finance_request/create/$', 'account_finance_request_create',name="account_finance_request_create"),
    
    #AJAX SECTIONS
    url(r'^ajax_delete_folder/$','ajax_delete_folder'),
    url(r'^ajax_delete_file/$','ajax_delete_file'),
    
    # url(r'^GCP/', include('GCP.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

