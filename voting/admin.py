from django.contrib import admin
from .models import Question, Vote, ShortAnswerResponse

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'question_type', 'simple_code', 'is_active', 'show_results', 'total_votes', 'created_at']
    list_filter = ['is_active', 'show_results', 'question_type', 'created_at']
    search_fields = ['text', 'simple_code']
    readonly_fields = ['id', 'created_at', 'simple_code']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['question', 'choice', 'client_fingerprint', 'created_at']
    list_filter = ['choice', 'created_at']
    readonly_fields = ['created_at']

@admin.register(ShortAnswerResponse)
class ShortAnswerResponseAdmin(admin.ModelAdmin):
    list_display = ['question', 'response_text', 'client_fingerprint', 'created_at']
    list_filter = ['created_at']
    search_fields = ['response_text', 'question__text']
    readonly_fields = ['created_at']
