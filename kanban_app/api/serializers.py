"""Serializers for kanban app models."""
from rest_framework import serializers
from kanban_app.models import Board, Task, Comment
from auth_app.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data in responses."""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']


class BoardListSerializer(serializers.ModelSerializer):
    """Serializer for board list view with aggregated counts."""
    
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    
    class Meta:
        model = Board
        fields = ['id', 'title', 'member_count', 'ticket_count', 
                  'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id']
    
    def get_member_count(self, obj):
        """Return number of board members."""
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        """Return total number of tasks."""
        return obj.tasks.count()
    
    def get_tasks_to_do_count(self, obj):
        """Return number of tasks with to-do status."""
        return obj.tasks.filter(status='to-do').count()
    
    def get_tasks_high_prio_count(self, obj):
        """Return number of high priority tasks."""
        return obj.tasks.filter(priority='high').count()


class BoardCreateSerializer(serializers.ModelSerializer):
    """Serializer for board creation with member assignment."""
    
    members = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True
    )
    
    class Meta:
        model = Board
        fields = ['title', 'members']
    
    def create(self, validated_data):
        """Create board and assign members."""
        member_ids = validated_data.pop('members')
        board = Board.objects.create(
            title=validated_data['title'],
            owner=self.context['request'].user
        )
        board.members.set(User.objects.filter(id__in=member_ids))
        return board


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for task with assignee and reviewer details."""
    
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    assignee_id = serializers.IntegerField(
        write_only=True, 
        required=False, 
        allow_null=True
    )
    reviewer_id = serializers.IntegerField(
        write_only=True, 
        required=False, 
        allow_null=True
    )
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 
                  'assignee', 'reviewer', 'assignee_id', 'reviewer_id', 
                  'due_date', 'comments_count', 'board']
    
    def get_comments_count(self, obj):
        """Return number of comments on task."""
        return obj.comments.count()


class BoardDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed board view with members and tasks."""
    
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for task comments."""
    
    author = serializers.CharField(
        source='author.fullname', 
        read_only=True
    )
    
    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['created_at']