from django.urls import path, include
from rest_framework.routers import DefaultRouter
from kanban_app.api.views import (
    BoardViewSet, TaskViewSet, 
    CommentListCreateView, CommentDeleteView
)

router = DefaultRouter()
router.register('boards', BoardViewSet, basename='board')
router.register('tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'tasks/<int:task_id>/comments/', 
        CommentListCreateView.as_view(), 
        name='comment-list'
    ),
    path(
        'tasks/<int:task_id>/comments/<int:comment_id>/', 
        CommentDeleteView.as_view(), 
        name='comment-delete'
    ),
]