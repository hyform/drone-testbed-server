"""design URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from . import views

admin.autodiscover()
admin.site.enable_nav_sidebar = False

#router = routers.DefaultRouter()
#router.register(r'users', repo.views.UserViewSet)
#router.register(r'groups', repo.views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLS for the browsable API.

admin.autodiscover()
admin.site.enable_nav_sidebar = False

urlpatterns = [
    path('repo/', include('repo.urls')),
    path('ai/', include('ai.urls')),
    path('exper/', include('exper.urls')),
    path('process/', include('process.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('', views.ateams_homepage, name='home'),
    path('chat/', include('chat.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('design/', views.ateams_design, name='design'),
    path('ops/', views.ateams_ops, name='ops'),
    path('business/', views.ateams_business, name='business'),
    path('process/', views.ateams_process, name='process'),
    path('experiment/', views.ateams_experiment, name='experiment'),
    path('setup/', views.ateams_setup, name='setup'),
    path('presession/', views.ateams_presession, name='presession'),
    path('postsession/', views.ateams_postsession, name='postsession'),
    path('experimentchat/', views.ateams_experiment_chat, name='experimentchat'),
    path('tempuserinfo/', views.ateams_temp_user_info, name='tempuserinfo'),
    path('info/', views.ateams_info, name='info'),
    path('ateams_main/', views.ateams_main, name="ateams_main"),
    path('structure/', views.structure, name="structure"),
]
