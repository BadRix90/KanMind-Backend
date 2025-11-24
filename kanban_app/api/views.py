"""
API views for Kanban board management.
Provides CRUD operations for boards, tasks, and comments with permission checks.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import models
from kanban_app.models import Board, Task, Comment
from kanban_app.api.serializers import (
    BoardListSerializer, BoardCreateSerializer,
    BoardDetailSerializer, TaskSerializer, CommentSerializer
)
from auth_app.models import User


class BoardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'create':
            return BoardCreateSerializer
        if self.action == 'retrieve':
            return BoardDetailSerializer
        return BoardListSerializer

    def create(self, request):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            board = serializer.save()
            response_serializer = BoardListSerializer(board)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def retrieve(self, request, pk=None):
        try:
            board = Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            return Response(
                {'error': 'Board not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        is_member = board.members.filter(id=request.user.id).exists()
        is_owner = board.owner == request.user
        
        if not (is_member or is_owner):
            return Response(
                {'error': 'Not a board member'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = BoardDetailSerializer(board)
        return Response(serializer.data)

    def update(self, request, pk=None, partial=False):
        try:
            board = Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            return Response(
                {'error': 'Board not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        is_member = board.members.filter(id=request.user.id).exists()
        is_owner = board.owner == request.user
        
        if not (is_member or is_owner):
            return Response(
                {'error': 'Not a board member'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        title = request.data.get('title', board.title)
        member_ids = request.data.get('members', [])
        
        board.title = title
        board.save()
        
        if member_ids:
            board.members.set(User.objects.filter(id__in=member_ids))
        
        owner_data = {
            'id': board.owner.id,
            'email': board.owner.email,
            'fullname': board.owner.fullname
        }
        members_data = [
            {'id': m.id, 'email': m.email, 'fullname': m.fullname}
            for m in board.members.all()
        ]
        
        return Response({
            'id': board.id,
            'title': board.title,
            'owner_data': owner_data,
            'members_data': members_data
        })
    
    def destroy(self, request, pk=None):
        try:
            board = Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            return Response(
                {'error': 'Board not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if board.owner != request.user:
            return Response(
                {'error': 'Not board owner'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        boards = Board.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        )
        return Task.objects.filter(board__in=boards)

    def create(self, request):
        board_id = request.data.get('board')
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return Response(
                {'error': 'Board not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        is_member = board.members.filter(id=request.user.id).exists()
        is_owner = board.owner == request.user
        
        if not (is_member or is_owner):
            return Response(
                {'error': 'Not a board member'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save(created_by=request.user)

            if 'assignee_id' in request.data:
                task.assignee_id = request.data['assignee_id']
            if 'reviewer_id' in request.data:
                task.reviewer_id = request.data['reviewer_id']
            task.save()

            response_serializer = TaskSerializer(task)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def retrieve(self, request, pk=None):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        is_member = task.board.members.filter(id=request.user.id).exists()
        is_owner = task.board.owner == request.user
        
        if not (is_member or is_owner):
            return Response(
                {'error': 'Not a board member'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def update(self, request, pk=None, partial=False):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        is_member = task.board.members.filter(id=request.user.id).exists()
        is_owner = task.board.owner == request.user
        
        if not (is_member or is_owner):
            return Response(
                {'error': 'Not a board member'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(
            task,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()

            if 'assignee_id' in request.data:
                task.assignee_id = request.data['assignee_id']
            if 'reviewer_id' in request.data:
                task.reviewer_id = request.data['reviewer_id']
            task.save()

            return Response(TaskSerializer(task).data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def destroy(self, request, pk=None):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        is_creator = task.created_by == request.user
        is_board_owner = task.board.owner == request.user
        
        if not (is_creator or is_board_owner):
            return Response(
                {'error': 'Not authorized to delete this task'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request):
        tasks = self.get_queryset().filter(assignee=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewing(self, request):
        tasks = self.get_queryset().filter(reviewer=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class CommentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        is_member = task.board.members.filter(id=request.user.id).exists()
        is_owner = task.board.owner == request.user
        
        if not (is_member or is_owner):
            return Response(
                {'error': 'Not a board member'},
                status=status.HTTP_403_FORBIDDEN
            )

        comments = task.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        is_member = task.board.members.filter(id=request.user.id).exists()
        is_owner = task.board.owner == request.user
        
        if not (is_member or is_owner):
            return Response(
                {'error': 'Not a board member'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(task=task, author=request.user)
            return Response(
                CommentSerializer(comment).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, task_id, comment_id):
        try:
            comment = Comment.objects.get(
                id=comment_id,
                task_id=task_id
            )
        except Comment.DoesNotExist:
            return Response(
                {'error': 'Comment not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if comment.author != request.user:
            return Response(
                {'error': 'Not comment author'},
                status=status.HTTP_403_FORBIDDEN
            )

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)