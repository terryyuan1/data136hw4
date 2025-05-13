import requests
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Post, Comment

class EndpointTestCase(TestCase):
    """Test case for API endpoints"""
    
    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='adminpassword123'
        )
        self.admin_user.is_staff = True
        self.admin_user.save()
        
        # Create a regular user
        self.user = User.objects.create_user(
            username='user_test',
            email='user@test.com',
            password='userpassword123'
        )
        
        # Create a test post
        self.post = Post.objects.create(
            author=self.admin_user,
            title='Test Post',
            content='This is a test post content'
        )
        
        # Create a test comment
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='This is a test comment'
        )
        
        # Set up the test client
        self.client = Client()
    
    def test_authentication_requirements(self):
        """Test that endpoints enforce authentication requirements"""
        # Test new_post requires authentication
        response = self.client.get('/app/new_post/')
        self.assertEqual(response.status_code, 401)
        
        # Test new_comment requires authentication
        response = self.client.get('/app/new_comment/')
        self.assertEqual(response.status_code, 401)
        
        # Test createPost requires authentication
        response = self.client.post('/app/createPost/', {'title': 'New Post', 'content': 'Content'})
        self.assertEqual(response.status_code, 401)
        
        # Test createComment requires authentication
        response = self.client.post('/app/createComment/', {'post_id': self.post.id, 'content': 'Comment'})
        self.assertEqual(response.status_code, 401)
        
        # Test hidePost requires admin authentication
        response = self.client.post('/app/hidePost/', {'post_id': self.post.id, 'reason': 'Test reason'})
        self.assertEqual(response.status_code, 401)
        
        # Test hideComment requires admin authentication
        response = self.client.post('/app/hideComment/', {'comment_id': self.comment.id, 'reason': 'Test reason'})
        self.assertEqual(response.status_code, 401)
    
    def test_authenticated_user_access(self):
        """Test that authenticated non-admin users can access appropriate endpoints"""
        # Login as regular user
        self.client.login(username='user_test', password='userpassword123')
        
        # Test new_post accessible to authenticated user
        response = self.client.get('/app/new_post/')
        self.assertEqual(response.status_code, 200)
        
        # Test new_comment accessible to authenticated user
        response = self.client.get('/app/new_comment/')
        self.assertEqual(response.status_code, 200)
        
        # Test createPost works for authenticated user
        response = self.client.post('/app/createPost/', {'title': 'User Post', 'content': 'User content'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(title='User Post').exists())
        
        # Test createComment works for authenticated user
        response = self.client.post('/app/createComment/', {'post_id': self.post.id, 'content': 'User comment'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(content='User comment').exists())
        
        # Test hidePost requires admin (should fail for regular user)
        response = self.client.post('/app/hidePost/', {'post_id': self.post.id, 'reason': 'Test reason'})
        self.assertEqual(response.status_code, 401)
        
        # Test hideComment requires admin (should fail for regular user)
        response = self.client.post('/app/hideComment/', {'comment_id': self.comment.id, 'reason': 'Test reason'})
        self.assertEqual(response.status_code, 401)
    
    def test_admin_access(self):
        """Test that admin users can access all endpoints"""
        # Login as admin
        self.client.login(username='admin_test', password='adminpassword123')
        
        # Test admin can hide post
        response = self.client.post('/app/hidePost/', {'post_id': self.post.id, 'reason': 'Admin hide reason'})
        self.assertEqual(response.status_code, 200)
        
        # Verify post is hidden
        self.post.refresh_from_db()
        self.assertTrue(self.post.is_hidden)
        self.assertEqual(self.post.hide_reason, 'Admin hide reason')
        
        # Test admin can hide comment
        response = self.client.post('/app/hideComment/', {'comment_id': self.comment.id, 'reason': 'Admin hide reason'})
        self.assertEqual(response.status_code, 200)
        
        # Verify comment is hidden
        self.comment.refresh_from_db()
        self.assertTrue(self.comment.is_hidden)
        self.assertEqual(self.comment.hide_reason, 'Admin hide reason')
        
        # Test dumpFeed for admin
        response = self.client.get('/app/dumpFeed/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_dump_feed_format(self):
        """Test that dumpFeed returns data in the correct format"""
        # Login as admin
        self.client.login(username='admin_test', password='adminpassword123')
        
        # Get feed data
        response = self.client.get('/app/dumpFeed/')
        self.assertEqual(response.status_code, 200)
        
        # Check response format
        data = response.json()
        self.assertIsInstance(data, list)
        
        if len(data) > 0:
            first_post = data[0]
            self.assertIn('id', first_post)
            self.assertIn('username', first_post)
            self.assertIn('date', first_post)
            self.assertIn('title', first_post)
            self.assertIn('content', first_post)
            self.assertIn('comments', first_post)
            self.assertIsInstance(first_post['comments'], list) 