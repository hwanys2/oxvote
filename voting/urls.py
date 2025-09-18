from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('qr/<uuid:question_id>/', views.qr_page, name='qr_page'),
    path('vote/<uuid:question_id>/', views.vote_page, name='vote_page'),
    path('result/<uuid:question_id>/', views.vote_result, name='vote_result'),
    path('api/toggle-results/<uuid:question_id>/', views.toggle_results, name='toggle_results'),
    path('api/stats/<uuid:question_id>/', views.get_vote_stats, name='vote_stats'),
    path('privacy/', views.privacy, name='privacy'),
]
