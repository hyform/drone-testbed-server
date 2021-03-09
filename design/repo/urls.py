from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib.auth.decorators import login_required
from repo import views

app_name = 'repo'

urlpatterns = [
    # path('user/', views.UserViewSet.as_view({'get': 'list'})),
    # path('team/', views.TeamList.as_view()),
    path('vehicle/', views.VehicleList.as_view()),
    path('vehicle/<int:pk>/', views.VehicleDetail.as_view()),
    path('scenario/', views.ScenarioDetail.as_view()),
    path('scenario/<int:ver>/', views.ScenarioDetail.as_view()),
    # path('path/', views.PathList.as_view()),
    # path('path/<int:pk>/', views.PathDetail.as_view()),
    path('plan/', views.PlanList.as_view()),
    path('plan2/', views.Plan2List.as_view()),
    path('planshort/', views.PlanShortList.as_view()),
    path('plan/<int:pk>/', views.PlanDetail.as_view()),
    path('vehicledemo/', views.VDList.as_view()),
    path('vehicledemo/<int:pk>/', views.VDDetail.as_view()),
    path('scenariodemo/', views.SDList.as_view()),
    path('scenariodemo/<int:pk>/', views.SDDetail.as_view()),
    path('opsplandemo/', views.OPDList.as_view()),
    path('opsplandemo/<int:pk>/', views.OPDDetail.as_view()),
    path('playdemo/', views.PDList.as_view()),
    path('playdemo/<int:pk>/', views.PDDetail.as_view()),
    path('datalog/', views.DataLogList.as_view()),
    path('sessiondatalog/', views.SessionDataLog.as_view()),
    # path('datalog/<int:pk>', views.DataLogDetail.as_view()),
    path('datalog/list/<int:session_id>/', views.DataLogListView.as_view()),
    path('mediator/count/<int:session_id>/', views.MediationCountView.as_view()),
    path('mediator/count/<int:session_id>/section/<int:section_id>/', views.MediationCountView.as_view()),
    path('mediator/chat/<int:session_id>/section/<int:section_id>/', views.MediationChatView.as_view()),
    # path('datalog/admin', views.DLAdminView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
