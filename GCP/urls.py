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
    url(r'^superuser/$', 'superuser', name='superuser'),
    url(r'^superuser/verify$', 'superuser_verify', name='superuser_verify'),
    
    #ACCOUNT SECTION
    url(r'^account/profile/$', 'account_profile', name='account_profile'),
    url(r'^account/profile/edit/$', 'account_edit', name='account_edit'),
    url(r'^account/profile/delete/$', 'account_delete', name='account_delete'),
    url(r'^account/settings/$', 'account_settings', name='account_settings'),
    url(r'^account/files/(?P<folder_id>\d+)/$', 'account_files'),
    
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

