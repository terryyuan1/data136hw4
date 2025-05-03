from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseBadRequest
from .forms import SignUpForm
from django.views.decorators.csrf import csrf_exempt




def index(request):
    context = {
        'bio': "Hi, I’m <b>Your Name</b> and my teammates are Alice & Bob.",
        'current_user': request.user if request.user.is_authenticated else None,
        'current_time': timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return render(request, 'app/index.html', context)


def new_user(request):
    """Display the signup form on GET."""
    form = SignUpForm()
    return render(request, 'app/new.html', {'form': form})


@csrf_exempt
def create_user(request):
    if request.method != "POST":
        return JsonResponse({ "error": "POST required" }, status=405)

    username = request.POST.get("username")
    email    = request.POST.get("email")
    password = request.POST.get("password")

    # … your user‐creation logic here …

    return JsonResponse({ "message": "User created successfully." })