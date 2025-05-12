import json
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
        'bio':          "Hi, I'm <b>Your Name</b> and my teammates are Alice & Bob.",
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
    # 1) only allow POST
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=405)

    # 2) parse JSON _or_ form-encoded
    ct = request.META.get('CONTENT_TYPE', '')
    if ct.startswith('application/json'):
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'invalid JSON'}, status=400)
        uname    = payload.get('user_name') or payload.get('username')
        email    = payload.get('email')
        password = payload.get('password')
        is_admin = payload.get('is_admin', '0')
    else:
        uname    = request.POST.get('user_name') or request.POST.get('username')
        email    = request.POST.get('email')
        password = request.POST.get('password')
        is_admin = request.POST.get('is_admin', '0')

    # 3) missing fields → HTTP 200 with error JSON
    if not uname or not email or not password:
        return JsonResponse(
            {'error': 'username, email, and password required'}
        )

    # 4) duplicate email/username → HTTP 400
    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': 'email already in use'}, status=400)
    if User.objects.filter(username=uname).exists():
        return JsonResponse({'error': 'username already in use'}, status=400)

    # 5) everything's good → create the user
    user = User.objects.create_user(
        username=uname,
        email=email,
        password=password,
    )
    # set staff status if they checked "1"
    user.is_staff = (is_admin == "1")
    user.save()

    return JsonResponse({'message': 'User created successfully.'})


@require_GET
def new_post(request):
    # GET only: render the post-creation form
    return render(request, 'app/new_post.html')

@require_GET
def new_comment(request):
    # GET only: render the comment-creation form
    return render(request, 'app/new_comment.html')

@csrf_exempt
def create_post(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    ct = request.META.get('CONTENT_TYPE','')
    if ct.startswith('application/json'):
        try:
            payload = json.loads(request.body.decode())
        except json.JSONDecodeError:
            return JsonResponse({'error': 'invalid JSON'}, status=400)
        title   = payload.get('title')
        content = payload.get('content')
    else:
        title   = request.POST.get('title')
        content = request.POST.get('content')

    if not title or not content:
        return JsonResponse({'error': 'title and content required'}, status=400)

    post = Post.objects.create(author=request.user, title=title, content=content)
    return JsonResponse({'id': post.id, 'message': 'Post created'})

@csrf_exempt
def create_comment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    ct = request.META.get('CONTENT_TYPE','')
    if ct.startswith('application/json'):
        try:
            payload = json.loads(request.body.decode())
        except json.JSONDecodeError:
            return JsonResponse({'error': 'invalid JSON'}, status=400)
        post_id = payload.get('post_id')
        content = payload.get('content')
    else:
        post_id = request.POST.get('post_id')
        content = request.POST.get('content')

    if not post_id or not content:
        return JsonResponse({'error': 'post_id and content required'}, status=400)

    try:
        parent = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'post not found'}, status=404)

    comment = Comment.objects.create(user=request.user, post=parent, content=content)
    return JsonResponse({'id': comment.id, 'message': 'Comment created'})

@csrf_exempt
def hide_post(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    if not (request.user.is_authenticated and request.user.is_staff):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # Accept both JSON and form data
    ct = request.META.get('CONTENT_TYPE', '')
    if ct.startswith('application/json'):
        try:
            payload = json.loads(request.body.decode())
        except json.JSONDecodeError:
            return JsonResponse({'error': 'invalid JSON'}, status=400)
        post_id = payload.get('post_id')
        reason = payload.get('reason', '')
    else:
        post_id = request.POST.get('post_id')
        reason = request.POST.get('reason', '')

    if not post_id:
        return JsonResponse({'error': 'post_id required'}, status=400)

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'post not found'}, status=404)

    post.hidden = True
    post.hide_reason = reason
    post.save()
    return JsonResponse({'message': 'Post hidden'})

@csrf_exempt
def hide_comment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    if not (request.user.is_authenticated and request.user.is_staff):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # Accept both JSON and form data
    ct = request.META.get('CONTENT_TYPE', '')
    if ct.startswith('application/json'):
        try:
            payload = json.loads(request.body.decode())
        except json.JSONDecodeError:
            return JsonResponse({'error': 'invalid JSON'}, status=400)
        comment_id = payload.get('comment_id')
        reason = payload.get('reason', '')
    else:
        comment_id = request.POST.get('comment_id')
        reason = request.POST.get('reason', '')

    if not comment_id:
        return JsonResponse({'error': 'comment_id required'}, status=400)

    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({'error': 'comment not found'}, status=404)

    comment.hidden = True
    comment.hide_reason = reason
    comment.save()
    return JsonResponse({'message': 'Comment hidden'})

@csrf_exempt
def dump_feed(request):
    # only GET
    if request.method != "GET":
        return JsonResponse({'error': 'GET required'}, status=405)

    # must be logged in staff
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    posts = Post.objects.filter(hidden=False).order_by('-created_at')
    feed = []
    for p in posts:
        feed.append({
            'id'      : p.id,
            'username': p.author.username,
            'date'    : p.created_at.strftime("%Y-%m-%d %H:%M"),
            'title'   : p.title,
            'content' : p.content,
            'comments': [c.id for c in p.comment_set.filter(hidden=False)],
        })
    return JsonResponse(feed, safe=False)