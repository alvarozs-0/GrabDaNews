from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Article, CustomUser, Publisher
from .utils import (verify_username, verify_password, verify_email,
                    verify_role_publisher)


# Create your views here.
def home(request):
    """
    Home view for the news application.
    """
    # Show recent approved articles
    recent_articles = Article.objects.filter(status='approved').order_by(
        '-published_at')[:5]

    context = {
        'recent_articles': recent_articles
    }
    return render(request, 'news/home.html', context)


def login_user(request):
    """
    Authenticate and log in a user.
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, 'news/login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'news/login.html')

    return render(request, 'news/login.html')


def logout_user(request):
    """
    Logout view for the news application.
    """
    if request.user.is_authenticated:
        messages.success(request, "You have been logged out successfully.")
        logout(request)
    return redirect('login_user')


def register(request):
    """
    Handles user registration by verifying all fields and creating a new user.
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        role = request.POST.get('role', '').strip()
        # Get list of publisher IDs
        publisher_ids = request.POST.getlist('publishers')

        # Check required fields
        required_fields = [
            username, email, first_name, last_name,
            password, confirm_password, role
        ]
        if not all(required_fields):
            messages.error(request, "All fields are required.")
            context = {
                'publishers': Publisher.objects.all(),
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'publisher_ids': publisher_ids
            }
            return render(request, 'news/register.html', context)

        # Verify username
        if not verify_username(username):
            messages.error(request, "Username is invalid or already taken.")
            context = {
                'publishers': Publisher.objects.all(),
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'publisher_ids': publisher_ids
            }
            return render(request, 'news/register.html', context)

        # Verify email
        if not verify_email(email):
            messages.error(request, "Email is invalid or already registered.")
            context = {
                'publishers': Publisher.objects.all(),
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'publisher_ids': publisher_ids
            }
            return render(request, 'news/register.html', context)

        # Verify password
        if not verify_password(password):
            messages.error(
                request, "Password is too weak. Password must be at "
                "least 8 characters long and contain both "
                "letters and numbers."
            )
            context = {
                'publishers': Publisher.objects.all(),
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'publisher_ids': publisher_ids
            }
            return render(request, 'news/register.html', context)

        # Check password confirmation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            context = {
                'publishers': Publisher.objects.all(),
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'publisher_ids': publisher_ids
            }
            return render(request, 'news/register.html', context)

        # Verify role and publisher combination
        is_valid, error_msg = verify_role_publisher(role, publisher_ids)
        if not is_valid:
            messages.error(request, error_msg)
            context = {
                'publishers': Publisher.objects.all(),
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'publisher_ids': publisher_ids
            }
            return render(request, 'news/register.html', context)

        try:
            # Create the user
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role
            )

            # Set publishers if provided
            if publisher_ids:
                publishers = Publisher.objects.filter(id__in=publisher_ids)
                if role == 'reader':
                    # For readers, set as subscriptions
                    user.subscribed_publishers.set(publishers)
                else:
                    # For editors/journalists, set as work affiliation
                    user.publishers.set(publishers)

            user.save()

            # Add user to appropriate group based on role
            if role:
                group, created = Group.objects.get_or_create(name=role)
                user.groups.add(group)

            messages.success(
                request, "Registration successful! You can now log in."
            )
            return redirect('login_user')

        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            context = {
                'publishers': Publisher.objects.all(),
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'publisher_ids': publisher_ids
            }
            return render(request, 'news/register.html', context)

    # GET request - show form with publishers
    context = {
        'publishers': Publisher.objects.all()
    }
    return render(request, 'news/register.html', context)


def article_detail(request, article_id):
    """
    View to display details of a specific article.
    """
    article = get_object_or_404(Article, id=article_id)

    # Check if user can view this article
    if article.status != 'approved' and request.user != article.author:
        # Only allow author and editors to view non-approved articles
        if not (request.user.is_authenticated and
                request.user.role == 'editor'):
            messages.error(request, "Article not found or access denied.")
            return redirect('home')

    return render(request, 'news/article_detail.html', {'article': article})


# =============================================================================
# ARTICLE MANAGEMENT VIEWS
# =============================================================================

@login_required
def article_list(request):
    """
    List articles based on user role and permissions.
    """
    user = request.user

    if user.role == 'journalist':
        # Journalists see their own articles
        articles = Article.objects.filter(author=user)
    elif user.role == 'editor':
        # Editors see articles from their affiliated publishers
        if user.publishers.exists():
            articles = Article.objects.filter(
                Q(publisher__in=user.publishers.all()) | Q(publisher=None)
            )
        else:
            articles = Article.objects.filter(publisher=None)
    else:
        # Readers see only approved articles
        articles = Article.objects.filter(status='approved')

    # Pagination
    paginator = Paginator(articles, 10)  # Show 10 articles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'articles': page_obj,
        'user_role': user.role if user.is_authenticated else None
    }

    return render(request, 'news/article_list.html', context)


@login_required
def create_article(request):
    """
    Create a new article (journalists only).
    """
    if request.user.role != 'journalist':
        messages.error(request, "Only journalists can create articles.")
        return redirect('article_list')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        publisher_id = request.POST.get('publisher', '').strip()

        # Validation
        if not title or not content:
            messages.error(request, "Title and content are required.")
            context = {
                'title': title,
                'content': content,
                'publisher_id': publisher_id,
                'publishers': request.user.publishers.all()
            }
            return render(request, 'news/create_article.html', context)

        try:
            # Create article
            article = Article.objects.create(
                title=title,
                content=content,
                author=request.user,
                status='submitted'
            )

            # Set publisher if provided
            if publisher_id:
                try:
                    publisher = Publisher.objects.get(id=publisher_id)
                    # Verify journalist is affiliated with this publisher
                    if publisher in request.user.publishers.all():
                        article.publisher = publisher
                    else:
                        # Allow independent submission
                        article.publisher = None
                except Publisher.DoesNotExist:
                    article.publisher = None

            article.save()

            messages.success(request, "Article submitted successfully!")
            return redirect('article_detail', article_id=article.id)

        except Exception as e:
            messages.error(request, f"Error creating article: {str(e)}")

    # GET request - show form
    context = {
        'publishers': request.user.publishers.all()
    }
    return render(request, 'news/create_article.html', context)


@login_required
def edit_article(request, article_id):
    """
    Edit an existing article.
    """
    article = get_object_or_404(Article, id=article_id)

    # Permission check
    if request.user.role == 'journalist' and article.author != request.user:
        messages.error(request, "You can only edit your own articles.")
        return redirect('article_list')
    elif request.user.role == 'editor':
        # Editors can edit articles from their affiliated publishers
        if (article.publisher and
                article.publisher not in request.user.publishers.all()):
            messages.error(request, "You can only edit articles from your "
                           "affiliated publishers.")
            return redirect('article_list')
    else:
        messages.error(request, "Permission denied.")
        return redirect('article_list')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()

        if not title or not content:
            messages.error(request, "Title and content are required.")
        else:
            article.title = title
            article.content = content
            article.save()
            messages.success(request, "Article updated successfully!")
            return redirect('article_detail', article_id=article.id)

    return render(request, 'news/edit_article.html', {'article': article})


@login_required
def approve_article(request, article_id):
    """
    Approve or reject an article (editors only).
    """

    if request.user.role != 'editor':
        messages.error(request, "Only editors can approve articles.")
        return redirect('article_list')

    article = get_object_or_404(Article, id=article_id)

    # Check if editor can approve this article
    if (article.publisher and
            article.publisher not in request.user.publishers.all()):
        messages.error(request, "You can only approve articles from your "
                       "affiliated publishers.")
        return redirect('article_list')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            article.status = 'approved'
            article.approved_by = request.user
            article.published_at = timezone.now()
            messages.success(request, "Article approved and published!")
        elif action == 'reject':
            article.status = 'rejected'
            article.approved_by = request.user
            messages.success(request, "Article rejected.")

        article.save()
        return redirect('article_list')

    return render(request, 'news/approve_article.html', {'article': article})


@login_required
def delete_article(request, article_id):
    """
    Delete an article.
    """
    article = get_object_or_404(Article, id=article_id)

    # Permission check
    can_delete = False
    if request.user.role == 'journalist' and article.author == request.user:
        can_delete = True
    elif request.user.role == 'editor':
        if (not article.publisher or
                article.publisher in request.user.publishers.all()):
            can_delete = True

    if not can_delete:
        messages.error(request, "Permission denied.")
        return redirect('article_list')

    if request.method == 'POST':
        article_title = article.title
        article.delete()
        messages.success(request, f"Article '{article_title}' deleted "
                         f"successfully!")
        return redirect('article_list')

    return render(request, 'news/delete_article.html', {'article': article})
