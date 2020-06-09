from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from methods import views

app_name = 'methods'

urlpatterns = [
    path('getUserName/', views.getUserName),
    path('getTeamName/', views.getTeamName),

]

urlpatterns = format_suffix_patterns(urlpatterns)
