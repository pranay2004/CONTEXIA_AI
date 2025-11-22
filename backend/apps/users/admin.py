from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name')
    search_fields = ('user__username', 'user__email', 'company_name')
    readonly_fields = ('user',)
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Brand Settings', {
            'fields': ('company_name', 'target_audience', 'brand_voice')
        }),
        ('Analysis Data', {
            'fields': ('voice_fingerprint',),
            'classes': ('collapse',)
        }),
    )
