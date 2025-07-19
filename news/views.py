from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .models import Article


# Create your views here.
def home(request):
    """
    Home view for the news application.
    """
    return render(request, 'news/home.html')


def login_user(request):
    """
    Login view for the news application.
    """
    return render(request, 'news/login.html')


def logout_user(request):
    """
    Logout view for the news application.
    """
    # Logic for logging out the user would go here
    logout(request)
    return redirect('home')


def register(request):
    """
    Register view for the news application.
    """
    return render(request, 'news/register.html')


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
