from django.contrib import admin
from kanban_app.models import Board, Task, Comment


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Admin-Interface für Boards"""
    list_display = ['id', 'title', 'owner', 'member_count']
    search_fields = ['title', 'owner__email']
    list_filter = ['owner']
    filter_horizontal = ['members']
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin-Interface für Tasks"""
    list_display = ['id', 'title', 'board', 'status', 'priority', 
                    'assignee', 'reviewer', 'due_date']
    search_fields = ['title', 'description']
    list_filter = ['status', 'priority', 'board']
    date_hierarchy = 'due_date'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin-Interface für Comments"""
    list_display = ['id', 'task', 'author', 'created_at']
    search_fields = ['content', 'author__email']
    list_filter = ['created_at', 'author']
    readonly_fields = ['created_at']