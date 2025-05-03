from django.shortcuts import render, redirect
from datetime import datetime
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages

def test_view(request):
    return HttpResponse("This is a test view")

def index(request):
    """View function for the home page."""
    print("INDEX VIEW HIT!")
    context = {
        'current_user': request.user,
        'current_time': datetime.now().strftime("%A, %B %d, %Y %I:%M %p"),
        'bio': "We are a team of students working on HW4!"
    }
    return render(request, 'app/index.html', context)

def create_user(request):
    """Handle user creation form submission."""
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        
        # Validate data
        if not username or not password or not email:
            messages.error(request, 'All fields are required')
            return redirect('index')
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('index')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('index')
        
        # Create new user
        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            messages.success(request, f'User {username} created successfully!')
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
        
        return redirect('index')
    
    # If not POST, redirect to index
    return redirect('index')
