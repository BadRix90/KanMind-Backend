from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from auth_app.models import User
from kanban_app.models import Board, Task, Comment


class BoardTests(TestCase):
    """Tests für Board-Endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@test.de',
            fullname='Test User',
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_board(self):
        data = {'title': 'Test Board', 'members': [self.user.id]}
        response = self.client.post('/api/boards/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Board')
    
    def test_list_boards(self):
        Board.objects.create(
            title='Board 1', 
            owner=self.user
        )
        response = self.client.get('/api/boards/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_board_detail(self):
        board = Board.objects.create(
            title='Test', 
            owner=self.user
        )
        board.members.add(self.user)
        response = self.client.get(f'/api/boards/{board.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test')
    
    def test_update_board(self):
        board = Board.objects.create(
            title='Old', 
            owner=self.user
        )
        board.members.add(self.user)
        data = {'title': 'New', 'members': [self.user.id]}
        response = self.client.patch(
            f'/api/boards/{board.id}/', 
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'New')
    
    def test_delete_board_owner(self):
        board = Board.objects.create(
            title='Delete Me', 
            owner=self.user
        )
        response = self.client.delete(f'/api/boards/{board.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_delete_board_not_owner(self):
        other_user = User.objects.create_user(
            email='other@test.de',
            fullname='Other',
            password='pass'
        )
        board = Board.objects.create(
            title='Not Mine', 
            owner=other_user
        )
        response = self.client.delete(f'/api/boards/{board.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TaskTests(TestCase):
    """Tests für Task-Endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@test.de',
            fullname='Test User',
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        self.board = Board.objects.create(
            title='Test Board',
            owner=self.user
        )
        self.board.members.add(self.user)
    
    def test_create_task(self):
        data = {
            'board': self.board.id,
            'title': 'Test Task',
            'description': 'Test Description',
            'status': 'to-do',
            'priority': 'high',
            'due_date': '2025-12-31'
        }
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Task')
    
    def test_update_task(self):
        task = Task.objects.create(
            board=self.board,
            title='Old Task',
            status='to-do',
            priority='low',
            created_by=self.user
        )
        data = {'status': 'in-progress', 'priority': 'high'}
        response = self.client.patch(f'/api/tasks/{task.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'in-progress')
    
    def test_delete_task_creator(self):
        task = Task.objects.create(
            board=self.board,
            title='Delete Me',
            status='to-do',
            priority='low',
            created_by=self.user
        )
        response = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_get_assigned_tasks(self):
        Task.objects.create(
            board=self.board,
            title='Assigned to me',
            status='to-do',
            priority='low',
            assignee=self.user,
            created_by=self.user
        )
        response = self.client.get('/api/tasks/assigned-to-me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_reviewing_tasks(self):
        Task.objects.create(
            board=self.board,
            title='Review Task',
            status='review',
            priority='medium',
            reviewer=self.user,
            created_by=self.user
        )
        response = self.client.get('/api/tasks/reviewing/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class CommentTests(TestCase):
    """Tests für Comment-Endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@test.de',
            fullname='Test User',
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        self.board = Board.objects.create(
            title='Test Board',
            owner=self.user
        )
        self.board.members.add(self.user)
        self.task = Task.objects.create(
            board=self.board,
            title='Test Task',
            status='to-do',
            priority='low',
            created_by=self.user
        )
    
    def test_create_comment(self):
        data = {'content': 'Test Comment'}
        response = self.client.post(
            f'/api/tasks/{self.task.id}/comments/', 
            data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Test Comment')
    
    def test_list_comments(self):
        Comment.objects.create(
            task=self.task,
            author=self.user,
            content='Comment 1'
        )
        response = self.client.get(
            f'/api/tasks/{self.task.id}/comments/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_delete_comment_author(self):
        comment = Comment.objects.create(
            task=self.task,
            author=self.user,
            content='Delete Me'
        )
        response = self.client.delete(
            f'/api/tasks/{self.task.id}/comments/{comment.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_delete_comment_not_author(self):
        other_user = User.objects.create_user(
            email='other@test.de',
            fullname='Other',
            password='pass'
        )
        comment = Comment.objects.create(
            task=self.task,
            author=other_user,
            content='Not Mine'
        )
        response = self.client.delete(
            f'/api/tasks/{self.task.id}/comments/{comment.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
class PermissionTests(TestCase):
    """Tests für Permissions"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='user1@test.de',
            fullname='User 1',
            password='test1234'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.de',
            fullname='User 2',
            password='test1234'
        )
        self.board = Board.objects.create(
            title='Test Board',
            owner=self.user1
        )
        self.board.members.add(self.user1)
    
    def test_board_access_not_member(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/boards/{self.board.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_task_create_not_member(self):
        self.client.force_authenticate(user=self.user2)
        data = {
            'board': self.board.id,
            'title': 'Task',
            'status': 'to-do',
            'priority': 'low'
        }
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ModelTests(TestCase):
    """Tests für Models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.de',
            fullname='Test User',
            password='test1234'
        )
        self.board = Board.objects.create(
            title='Test Board',
            owner=self.user
        )
    
    def test_board_str(self):
        self.assertEqual(str(self.board), 'Test Board')
    
    def test_task_str(self):
        task = Task.objects.create(
            board=self.board,
            title='Test Task',
            status='to-do',
            priority='low',
            created_by=self.user
        )
        self.assertEqual(str(task), 'Test Task')
    
    def test_comment_str(self):
        task = Task.objects.create(
            board=self.board,
            title='Task',
            status='to-do',
            priority='low',
            created_by=self.user
        )
        comment = Comment.objects.create(
            task=task,
            author=self.user,
            content='Comment'
        )
        self.assertIn('Test User', str(comment))


class EdgeCaseTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@test.de',
            fullname='Test User',
            password='test1234'
        )
        self.client.force_authenticate(user=self.user)
        self.board = Board.objects.create(
            title='Test Board',
            owner=self.user
        )
        self.board.members.add(self.user)
    
    def test_create_task_invalid_board(self):
        data = {
            'board': 9999,
            'title': 'Task',
            'status': 'to-do',
            'priority': 'low'
        }
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_comment_invalid_task(self):
        response = self.client.get('/api/tasks/9999/comments/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_task_with_assignee(self):
        data = {
            'board': self.board.id,
            'title': 'Task',
            'status': 'to-do',
            'priority': 'low',
            'assignee_id': self.user.id
        }
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['assignee']['id'], self.user.id)
    
    def test_task_with_reviewer(self):
        data = {
            'board': self.board.id,
            'title': 'Task',
            'status': 'to-do',
            'priority': 'low',
            'reviewer_id': self.user.id
        }
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reviewer']['id'], self.user.id)