# CloudySky - Django Web Application

## Overview
CloudySky is a Django-based social media/blogging platform with user management, content creation, and moderation features.

## Features
- User registration and authentication
- Create and view posts
- Comment on posts
- Admin moderation (hiding posts/comments)
- API endpoints for all functionality

## API Endpoints
- `/app/createPost` - Create a new post (auth required)
- `/app/createComment` - Create a new comment on a post (auth required)
- `/app/hidePost` - Hide a post (admin only)
- `/app/hideComment` - Hide a comment (admin only)
- `/app/dumpFeed` - Get JSON data of all posts (admin only)

## HTML Views
- `/app/new_post` - Form to create a new post (auth required)
- `/app/new_comment` - Form to create a new comment (auth required)

## Setup
1. Clone the repository
2. Install dependencies:
   ```
   pip install django
   ```
3. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
5. Run the development server:
   ```
   python manage.py runserver
   ```

## Testing
Run tests with:
```
python manage.py test app.test_endpoints
```

## Requirements
- Python 3.x
- Django 5.x 