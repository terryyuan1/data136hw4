import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloudysky.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import Post, Comment

# Get the first user
user = User.objects.first()

if user:
    # Create a test post with ID 1
    post, created = Post.objects.get_or_create(
        id=1,
        defaults={
            'author': user,
            'title': 'Test Post',
            'content': 'This is a test post for the autograder.'
        }
    )
    
    if created:
        print(f"Created test post with ID 1")
    else:
        print(f"Post with ID 1 already exists")
else:
    print("No users found in the database. Please create a user first.") 