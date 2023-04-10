from django.contrib import admin
from .models import Testnet, Notifications
from .models import UserInfo, CheckList
from django_summernote.admin import SummernoteModelAdmin
"""
    This page allow admin to display the content of Tables
"""


@admin.register(Testnet)
class TestnetAdmin(SummernoteModelAdmin):
    """
    Allows admin to manage Testnet via the admin panel
    """
    list_filter = ('testnet_name', 'created_on')
    list_display = ('id', 'author', 'status_testnet', 'testnet_user',
                    'slug', 'slug_original', 'category', 'created_on')
    search_fields = ('testnet_name', 'description')
    summernote_fields = ('description', 'tasks_description')


@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    """
    Allows admin to manage user notifications via the admin panel
    """
    list_display = ('id', 'notification_owner', 'title', 'created_on', 'read')


@admin.register(UserInfo)
class NotificationsAdmin(admin.ModelAdmin):
    """
    Allows admin to manage UserInfo via the admin panel
    """
    list_display = ('id', 'user', 'exp', 'created_on')
