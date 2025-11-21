from rest_framework import permissions


class IsBoardMember(permissions.BasePermission):
    """User muss Board-Member oder Owner sein"""
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'members'):
            return (obj.members.filter(id=request.user.id).exists() 
                    or obj.owner == request.user)
        if hasattr(obj, 'board'):
            board = obj.board
            return (board.members.filter(id=request.user.id).exists() 
                    or board.owner == request.user)
        return False


class IsBoardOwner(permissions.BasePermission):
    """User muss Board-Owner sein"""
    
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsTaskCreatorOrBoardOwner(permissions.BasePermission):
    """User muss Task-Creator oder Board-Owner sein"""
    
    def has_object_permission(self, request, view, obj):
        return (obj.created_by == request.user 
                or obj.board.owner == request.user)


class IsCommentAuthor(permissions.BasePermission):
    """User muss Comment-Author sein"""
    
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user