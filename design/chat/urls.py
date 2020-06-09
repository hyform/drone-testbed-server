# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('channels/', views.ChannelList.as_view()),
    path('channels/<int:team_id>/', views.ChannelExperList.as_view()),
]
