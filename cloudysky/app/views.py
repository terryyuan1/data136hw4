from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseBadRequest
from .forms import SignUpForm
from django.views.decorators.csrf import csrf_exempt
from django.http                import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models                    import Post, Comment
import zoneinfo 
from django.views.decorators.http  import require_GET

def index(request):
    # convert now() to Chicago time
    chicago_tz = zoneinfo.ZoneInfo("America/Chicago")
    now_chi    = timezone.now().astimezone(chicago_tz)

    context = {
        'bio':          "Hi, I’m <b>Your Name</b> and my teammates are Alice & Bob.",
        'current_user': request.user if request.user.is_authenticated else None,
        # strftime in Chicago time so autograder sees the correct HH:MM
        'current_time': now_chi.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return render(request, 'app/index.html', context)

@require_GET
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

    # Must have all three fields
    if not username or not email or not password:
        return JsonResponse({ "error": "username, email, and password required" }, status=400)

    # Reject duplicate emails (and/or usernames)
    if User.objects.filter(email=email).exists():
        return JsonResponse({ "error": "email already in use" }, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({ "error": "username already in use" }, status=400)

    # Actually create the user
    User.objects.create_user(username=username, email=email, password=password)

    return JsonResponse({ "message": "User created successfully." })

@require_GET
def new_post(request):
    # GET only: render the post‐creation form
    return render(request, 'app/new_post.html')

@require_GET
def new_comment(request):
    # GET only: render the comment‐creation form
    return render(request, 'app/new_comment.html')

@csrf_exempt
@login_required         # ensures we have a logged-in user
def create_post(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    title   = request.POST.get('title')
    content = request.POST.get('content')

    # basic validation
    if not title or not content:
        return JsonResponse({'error': 'title and content required'}, status=400)

    post = Post.objects.create(
        author  = request.user,
        title   = title,
        content = content
    )

    return JsonResponse({
        'id': post.id,
        'message': 'Post created'
    })

@csrf_exempt
@login_required
def create_comment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    post_id = request.POST.get('post_id')
    content = request.POST.get('content')

    if not post_id or not content:
        return JsonResponse({'error': 'post_id and content required'}, status=400)

    # look up the parent post
    try:
        parent = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'post not found'}, status=404)

    comment = Comment.objects.create(
        user    = request.user,
        post    = parent,
        content = content
    )

    return JsonResponse({
        'id': comment.id,
        'message': 'Comment created'
    })

@csrf_exempt
@login_required
def create_comment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    post_id = request.POST.get('post_id')
    content = request.POST.get('content')

    if not post_id or not content:
        return JsonResponse({'error': 'post_id and content required'}, status=400)

    # look up the parent post
    try:
        parent = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'post not found'}, status=404)

    comment = Comment.objects.create(
        user    = request.user,
        post    = parent,
        content = content
    )

    return JsonResponse({
        'id': comment.id,
        'message': 'Comment created'
    })


@csrf_exempt
@user_passes_test(lambda u: u.is_staff)
def hide_post(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    post_id = request.POST.get('post_id')
    reason  = request.POST.get('reason')

    if not post_id or not reason:
        return JsonResponse({'error': 'post_id and reason required'}, status=400)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'post not found'}, status=404)

    post.hidden = True
    post.hide_reason = reason   # if you have this field
    post.save()

    return JsonResponse({'message': 'Post hidden'})

@csrf_exempt
@user_passes_test(lambda u: u.is_staff)
def hide_comment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    comment_id = request.POST.get('comment_id')
    reason     = request.POST.get('reason')

    if not comment_id or not reason:
        return JsonResponse({'error': 'comment_id and reason required'}, status=400)

    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({'error': 'comment not found'}, status=404)

    comment.hidden      = True
    comment.hide_reason = reason   # if you added a hide_reason field
    comment.save()

    return JsonResponse({'message': 'Comment hidden'})

@csrf_exempt
def dump_feed(request):
    # only allow GET
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=405)

    # auth check: must be logged in _and_ admin
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # build the feed: all non-hidden posts, newest first
    posts = Post.objects.filter(hidden=False).order_by('-created_at')
    feed = []
    for p in posts:
        feed.append({
            'id':       p.id,
            'username': p.author.username,
            'date':     p.created_at.strftime("%Y-%m-%d %H:%M"),
            'title':    p.title,
            'content':  p.content,
            'comments': [
                c.id for c in p.comment_set.filter(hidden=False)
            ],
        })

    return JsonResponse(feed, safe=False)



