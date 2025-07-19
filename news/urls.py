from django.urls import path
from .views import (
    home,
    login_user,
    logout_user,
    register,
    article_detail,
    article_list,
    create_article,
    edit_article,
    approve_article,
    delete_article,
)


urlpatterns = [
    # Authentication and registration
    path('', home, name='home'),
    path('login/', login_user, name='login_user'),
    path('register/', register, name='register'),
    path('logout/', logout_user, name='logout_user'),

    # Article management
    path('articles/', article_list, name='article_list'),
    path('articles/create/', create_article, name='create_article'),
    path('articles/<int:article_id>/', article_detail, name='article_detail'),
    path('articles/<int:article_id>/edit/', edit_article, name='edit_article'),
    path('articles/<int:article_id>/approve/', approve_article,
         name='approve_article'),
    path('articles/<int:article_id>/delete/', delete_article,
         name='delete_article'),
]
