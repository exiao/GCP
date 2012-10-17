import os, sys
BASE_ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path.append(BASE_ROOT)
sys.path.append(BASE_ROOT+'/GCP')
sys.path.append(BASE_ROOT+'/gcpapp')
os.environ['DJANGO_SETTINGS_MODULE'] = 'GCP.settings'
sys.path.append('/usr/local/lib/python2.7/dist-packages/django')
import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
