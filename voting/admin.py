from django.contrib import admin
from .models import Question, Vote

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'is_active', 'show_results', 'total_votes', 'created_at']
    list_filter = ['is_active', 'show_results', 'created_at']
    search_fields = ['text']
    readonly_fields = ['id', 'created_at']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['question', 'choice', 'ip_address', 'created_at']
    list_filter = ['choice', 'created_at']
    readonly_fields = ['created_at']
