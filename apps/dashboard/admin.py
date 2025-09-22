from django.contrib import admin
from .models import DashboardWidget, SystemNotification, UserNotificationRead


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'widget_type', 'position', 'is_visible', 'created_at')
    list_filter = ('widget_type', 'is_visible', 'created_at')
    search_fields = ('title', 'user__first_name', 'user__last_name')
    ordering = ['user', 'position']


@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'is_global', 'is_active', 'created_at', 'expires_at')
    list_filter = ('notification_type', 'is_global', 'is_active', 'created_at')
    search_fields = ('title', 'message')
    filter_horizontal = ('target_users',)
    date_hierarchy = 'created_at'


@admin.register(UserNotificationRead)
class UserNotificationReadAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('user__first_name', 'user__last_name', 'notification__title')
