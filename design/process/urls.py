from django.urls import path

from . import views

urlpatterns = [
    path('intervention/', views.intervention),
    path('elapsed_time/', views.elapsed_time),    
]
