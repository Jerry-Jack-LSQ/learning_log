from django.contrib import admin
from .models import Score, Money


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('created_at',)
    ordering = ('-score', '-created_at')


@admin.register(Money)
class MoneyAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'updated_at')
    search_fields = ('user__username',)
    list_filter = ('updated_at',)
    ordering = ('-updated_at',)
