from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('gcpapp.views',

    url(r'^$', 'home', name='home'),
    url(r'^about/$', 'about', name='about'),
    url(r'^resources/$', 'resources', name='resources'),
    url(r'^reports/$', 'reports', name='reports'),
    url(r'^contact/$', 'contact', name='contact'),
    url(r'^signup/$', 'signup', name='signup'),
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout', name='logout'),
    # url(r'^GCP/', include('GCP.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
