from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from .models import Article, CustomUser, Publisher
from .utils import (verify_username, verify_password, verify_email,
                    verify_role_publisher)


# Create your views here.
def home(request):
    """
    Home view for the news application.
    """
    return render(request, 'news/home.html')


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
    # Logic to retrieve the article by ID would go here
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        return redirect('home')

    return render(request, 'news/article_detail.html',
                  {'article': article})
