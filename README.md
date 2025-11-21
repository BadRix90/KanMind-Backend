# KanMind Backend

Django REST Framework backend for KanMind - a Kanban board management application.

## Features

- User authentication with token-based auth
- Board management with ownership and membership
- Task management with status tracking (to-do, in-progress, review, done)
- Priority levels (low, medium, high)
- Task assignments (assignee & reviewer)
- Comment system for tasks
- RESTful API with comprehensive permissions

## Tech Stack

- Django 5.2.8
- Django REST Framework 3.14.0
- SQLite (development)
- Token Authentication

## Installation

### Prerequisites

- Python 3.14+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`

## API Endpoints

### Authentication
- `POST /api/registration/` - Register new user
- `POST /api/login/` - User login

### Boards
- `GET /api/boards/` - List all boards
- `POST /api/boards/` - Create board
- `GET /api/boards/{id}/` - Board details
- `PATCH /api/boards/{id}/` - Update board
- `DELETE /api/boards/{id}/` - Delete board (owner only)

### Tasks
- `GET /api/tasks/assignee/` - Tasks assigned to current user
- `GET /api/tasks/reviewer/` - Tasks to review
- `POST /api/tasks/` - Create task
- `PATCH /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task

### Comments
- `GET /api/tasks/{task_id}/comments/` - List comments
- `POST /api/tasks/{task_id}/comments/` - Add comment
- `DELETE /api/tasks/{task_id}/comments/{id}/` - Delete comment

## Project Structure
```
backend/
├── core/                  # Project settings
├── auth_app/             # User authentication
│   ├── api/
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── models.py
├── kanban_app/           # Boards, Tasks, Comments
│   ├── api/
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── permissions.py
│   └── models.py
└── manage.py
```

## Admin Interface

Access the Django admin at `http://127.0.0.1:8000/admin/`

## Guest Account

For testing purposes:
- Email: `guest@kanmind.com`
- Password: `guest123`
- Token: `68d4ee7f8c886ae2f4f8c72119484ad9c9df5f6d`

## Development

- All functions follow max 14 lines guideline
- PEP8 compliant code
- Token-based authentication required for all endpoints (except login/registration)

## License

MIT License

## Author

Kay Dietrich
- Email: kontakt@kaydietrich.com