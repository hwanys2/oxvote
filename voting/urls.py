from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # 정적 페이지 (간단한 코드 패턴보다 먼저 정의)
    path('privacy/', views.privacy, name='privacy'),
    path('ads.txt', views.ads_txt, name='ads_txt'),
    # UUID 기반 URL - O/X 투표
    path('qr/<uuid:question_id>/', views.qr_page, name='qr_page'),
    path('vote/<uuid:question_id>/', views.vote_page, name='vote_page'),
    path('result/<uuid:question_id>/', views.vote_result, name='vote_result'),
    path('api/toggle-results/<uuid:question_id>/', views.toggle_results, name='toggle_results'),
    path('api/stats/<uuid:question_id>/', views.get_vote_stats, name='vote_stats'),
    path('api/end-vote/<uuid:question_id>/', views.end_vote, name='end_vote'),
    # UUID 기반 URL - 단답형
    path('short-answer/qr/<uuid:question_id>/', views.short_answer_qr_page, name='short_answer_qr_page'),
    path('short-answer/vote/<uuid:question_id>/', views.short_answer_vote_page, name='short_answer_vote_page'),
    path('api/short-answer-stats/<uuid:question_id>/', views.get_short_answer_stats, name='short_answer_stats'),
    # 간단한 코드 기반 URL - O/X 투표
    path('<str:simple_code>/', views.vote_by_code, name='vote_by_code'),
    path('qr/code/<str:simple_code>/', views.qr_page_by_code, name='qr_page_by_code'),
    path('result/code/<str:simple_code>/', views.vote_result_by_code, name='vote_result_by_code'),
    path('api/toggle-results/code/<str:simple_code>/', views.toggle_results_by_code, name='toggle_results_by_code'),
    path('api/stats/code/<str:simple_code>/', views.get_vote_stats_by_code, name='vote_stats_by_code'),
    path('api/end-vote/code/<str:simple_code>/', views.end_vote_by_code, name='end_vote_by_code'),
    # 간단한 코드 기반 URL - 단답형
    path('short-answer/qr/code/<str:simple_code>/', views.short_answer_qr_page_by_code, name='short_answer_qr_page_by_code'),
    path('api/short-answer-stats/code/<str:simple_code>/', views.get_short_answer_stats_by_code, name='short_answer_stats_by_code'),
]
