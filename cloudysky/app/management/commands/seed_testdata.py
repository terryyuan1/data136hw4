from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Post, Comment

class Command(BaseCommand):
    help = 'Seeds the database with test data'

    def handle(self, *args, **options):
        # Create test user if not exists
        if not User.objects.filter(username='testadmin').exists():
            user = User.objects.create_user(
                username='testadmin',
                email='admin@example.com',
                password='admin'
            )
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS('Created test admin user'))
        else:
            user = User.objects.get(username='testadmin')
            self.stdout.write(self.style.SUCCESS('Test admin user already exists'))

        # Create test post if not exists
        post, created = Post.objects.get_or_create(
            id=1,
            defaults={
                'author': user,
                'title': 'Test Post',
                'content': 'This is a test post for autograding.'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created test post'))
        else:
            self.stdout.write(self.style.SUCCESS('Test post already exists'))

        # Create test comment if not exists
        comment, created = Comment.objects.get_or_create(
            id=1,
            defaults={
                'post': post,
                'author': user,
                'content': 'This is a test comment for autograding.'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created test comment'))
        else:
            self.stdout.write(self.style.SUCCESS('Test comment already exists')) 