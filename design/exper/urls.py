# exper/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('session/active/', views.ActiveSessionList.as_view()),
    path('session/', views.ActiveSession.as_view()),
    path('exper_sessions/', views.ExperimenterSessions.as_view()),
    path('session/dump/<int:session_id>/', views.log_view),
    path('select_organization/', views.select_organization),
    path('select_study/', views.select_study),
    path('continue_to_experiment/', views.continue_to_experiment),
    path('change_selection/', views.change_selection),    
    path('session_status_play/', views.session_status_play),
    path('session_status_stop/', views.session_status_stop),
    path('session_status_archive/', views.session_status_archive),
    path('create_session_group/', views.create_session_group),
    path('change_org_password/', views.change_org_password),
    path('change_user_password/', views.change_user_password),
    path('pre_check/', views.pre_check),
    path('post_check/', views.post_check),
    path('session/vehicle/<int:session_id>/', views.VehicleList.as_view()),
    path('session/plan/<int:session_id>/', views.PlanList.as_view()),
    path('session/scenario/<int:session_id>/', views.ScenarioList.as_view()),
    path('create_structure/', views.create_structure),
]
