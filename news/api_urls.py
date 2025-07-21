"""
URL configuration for News API endpoints.

This module defines the URL patterns for the RESTful API endpoints.
"""
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .api_views import (
    ArticleListAPIView,
    ArticleDetailAPIView,
    PublisherListAPIView,
    PublisherDetailAPIView,
    PublisherArticlesAPIView,
    JournalistListAPIView,
    JournalistDetailAPIView,
    JournalistArticlesAPIView,
    SubscriptionFeedAPIView,
)

app_name = 'news_api'

urlpatterns = [
    # Article endpoints
    path('articles/', ArticleListAPIView.as_view(), name='article_list'),
    path('articles/<int:pk>/', ArticleDetailAPIView.as_view(),
         name='article_detail'),

    # Publisher endpoints
    path('publishers/', PublisherListAPIView.as_view(),
         name='publisher_list'),
    path('publishers/<int:pk>/', PublisherDetailAPIView.as_view(),
         name='publisher_detail'),
    path('publishers/<int:pk>/articles/', PublisherArticlesAPIView.as_view(),
         name='publisher_articles'),

    # Journalist endpoints
    path('journalists/', JournalistListAPIView.as_view(),
         name='journalist_list'),
    path('journalists/<int:pk>/', JournalistDetailAPIView.as_view(),
         name='journalist_detail'),
    path('journalists/<int:pk>/articles/', JournalistArticlesAPIView.as_view(),
         name='journalist_articles'),

    # Subscription feed
    path('subscription-feed/', SubscriptionFeedAPIView.as_view(),
         name='subscription_feed'),

    # Django REST Framework browsable API (for development/testing)
    path('auth/', include('rest_framework.urls')),
]

# Add format suffix patterns to support .json and .xml extensions
urlpatterns = format_suffix_patterns(urlpatterns)
