"""
API Views for the News application.
Provides RESTful endpoints for articles, publishers, and journalists.
"""
from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination

from .models import Article, CustomUser, Publisher
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    SubscriptionArticleSerializer,
    JournalistSerializer,
    PublisherSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# Base classes to reduce repetition
class BaseListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination


class BaseDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]


# Article Views
class ArticleListAPIView(BaseListView):
    serializer_class = ArticleListSerializer

    def get_queryset(self):
        queryset = Article.objects.filter(
            status='approved').order_by('-published_at')

        # Apply filters
        publisher_id = self.request.query_params.get('publisher_id')
        if publisher_id:
            queryset = queryset.filter(publisher_id=publisher_id)

        journalist_id = self.request.query_params.get('journalist_id')
        if journalist_id:
            queryset = queryset.filter(author_id=journalist_id)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )

        return queryset


class ArticleDetailAPIView(BaseDetailView):
    queryset = Article.objects.filter(status='approved')
    serializer_class = ArticleDetailSerializer


# Publisher Views
class PublisherListAPIView(BaseListView):
    queryset = Publisher.objects.all().order_by('name')
    serializer_class = PublisherSerializer


class PublisherDetailAPIView(BaseDetailView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class PublisherArticlesAPIView(BaseListView):
    serializer_class = ArticleListSerializer

    def get_queryset(self):
        return Article.objects.filter(
            publisher_id=self.kwargs['pk'],
            status='approved'
        ).order_by('-published_at')


# Journalist Views
class JournalistListAPIView(BaseListView):
    serializer_class = JournalistSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(
            role='journalist').order_by('username')


class JournalistDetailAPIView(BaseDetailView):
    serializer_class = JournalistSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(role='journalist')


class JournalistArticlesAPIView(BaseListView):
    serializer_class = ArticleListSerializer

    def get_queryset(self):
        return Article.objects.filter(
            author_id=self.kwargs['pk'],
            status='approved'
        ).order_by('-published_at')


# Subscription Feed
class SubscriptionFeedAPIView(BaseListView):
    serializer_class = SubscriptionArticleSerializer

    def get_queryset(self):
        user = self.request.user
        articles = Article.objects.filter(status='approved')

        # Get subscribed content
        publisher_articles = Article.objects.none()
        if hasattr(user, 'subscribed_publishers'):
            publisher_articles = articles.filter(
                publisher__in=user.subscribed_publishers.all()
            )

        journalist_articles = Article.objects.none()
        if hasattr(user, 'subscribed_journalists'):
            journalist_articles = articles.filter(
                author__in=user.subscribed_journalists.all()
            )

        # Combine and remove duplicates
        combined = (publisher_articles | journalist_articles).distinct()
        return combined.order_by('-published_at')
