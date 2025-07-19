from django.urls import path
from .views import (
    home,
    login_user,
    logout_user,
    register,
    article_detail,
)


urlpatterns = [

    # Authentication and registration
    path('', home, name='home'),
    path('login/', login_user, name='login_user'),
    path('register/', register, name='register'),
    path('logout/', logout_user, name='logout_user'),


    path('article/<int:article_id>/', article_detail, name='article_detail'),

]
