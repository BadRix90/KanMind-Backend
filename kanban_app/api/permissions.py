"""Custom permission classes for kanban app."""
from rest_framework import permissions


class IsBoardMember(permissions.BasePermission):
    """Permission check for board members or owners."""
    
    def has_object_permission(self, request, view, obj):
        """Check if user is board member or owner."""
        if hasattr(obj, 'members'):
            return (obj.members.filter(id=request.user.id).exists() 
                    or obj.owner == request.user)
        if hasattr(obj, 'board'):
            board = obj.board
            return (board.members.filter(id=request.user.id).exists() 
                    or board.owner == request.user)
        return False


class IsBoardOwner(permissions.BasePermission):
    """Permission check for board owners."""
    
    def has_object_permission(self, request, view, obj):
        """Check if user is board owner."""
        return obj.owner == request.user


class IsTaskCreatorOrBoardOwner(permissions.BasePermission):
    """Permission check for task creators or board owners."""
    
    def has_object_permission(self, request, view, obj):
        """Check if user is task creator or board owner."""
        return (obj.created_by == request.user 
                or obj.board.owner == request.user)


class IsCommentAuthor(permissions.BasePermission):
    """Permission check for comment authors."""
    
    def has_object_permission(self, request, view, obj):
        """Check if user is comment author."""
        return obj.author == request.user