from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from ai import views
from ai.seqtosql.dronebotseqtosql import DroneBotSeqToSQL

app_name = 'ai'

urlpatterns = [
    path('designer1/', views.Designer1List.as_view()),
    path('opsplan/', views.OpsPlan.as_view()),
    path('uavdesignasses/', views.UAVDesignAsses.as_view()),
    path('uavdesign2asses/', views.UAVDesign2Asses.as_view()),
    path('dronebot/', views.DroneBot.as_view()),
    path('opsservice/', views.OpsService.as_view()),
    path('design_evaluation/', views.design_evaluation),
    path('design_trajectory/', views.design_trajectory),
]

urlpatterns = format_suffix_patterns(urlpatterns)

dbs2s = DroneBotSeqToSQL()
