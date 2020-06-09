from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from ai import views

app_name = 'ai'

urlpatterns = [
    path('designer1/', views.Designer1List.as_view()),
    path('ops1/', views.OpsPlan1.as_view()),
    path('uavdesignasses/', views.UAVDesignAsses.as_view()),
    path('uavdesign2asses/', views.UAVDesign2Asses.as_view()),
    path('uavdesign2traj/', views.UAVDesign2Traj.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
