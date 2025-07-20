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
    my_subscriptions,
    newsletter_list,
    create_newsletter,
    journalist_list,
    subscribe_to_journalist,
    unsubscribe_from_journalist,
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

    # Subscription management
    path('subscriptions/', my_subscriptions, name='my_subscriptions'),
    path('journalists/', journalist_list, name='journalist_list'),
    path('journalists/<int:journalist_id>/subscribe/', subscribe_to_journalist,
         name='subscribe_to_journalist'),
    path('journalists/<int:journalist_id>/unsubscribe/',
         unsubscribe_from_journalist, name='unsubscribe_from_journalist'),

    # Newsletter management
    path('newsletters/', newsletter_list, name='newsletter_list'),
    path('newsletters/create/', create_newsletter, name='create_newsletter'),
]
