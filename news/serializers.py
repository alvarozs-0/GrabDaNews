"""
Serializers for the News API.

This module contains serializers for converting Django models to/from JSON/XML
formats for API consumption.
"""
from rest_framework import serializers
from .models import Article, CustomUser, Publisher


class PublisherSerializer(serializers.ModelSerializer):
    """
    Serializer for Publisher model.
    """
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'description']


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model when used as article author.
    """
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name',
                  'email']
        read_only_fields = ['id', 'username', 'first_name', 'last_name',
                            'email']

    def get_full_name(self, obj):
        """Return the full name of the user."""
        return obj.get_full_name() or obj.username


class ArticleListSerializer(serializers.ModelSerializer):
    """
    Serializer for Article model in list views (minimal data).
    """
    author = AuthorSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    content_preview = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content_preview', 'author', 'publisher',
            'status', 'created_at', 'published_at'
        ]
        read_only_fields = ['id', 'created_at', 'published_at']

    def get_content_preview(self, obj):
        """Return a preview of the article content (first 200 characters)."""
        if len(obj.content) > 200:
            return obj.content[:200] + '...'
        return obj.content


class ArticleDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Article model in detail views (full data).
    """
    author = AuthorSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    approved_by = AuthorSerializer(read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'author', 'publisher', 'status',
            'created_at', 'published_at', 'approved_by'
        ]
        read_only_fields = [
            'id', 'author', 'publisher', 'status', 'created_at',
            'published_at', 'approved_by'
        ]


class SubscriptionArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for articles in subscription feeds.
    Includes additional metadata for subscription context.
    """
    author = AuthorSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    subscription_type = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'author', 'publisher',
            'published_at', 'subscription_type'
        ]
        read_only_fields = ['id', 'published_at']

    def get_subscription_type(self, obj):
        """
        Determine the subscription type based on the requesting user's
        subscriptions.
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None

        user = request.user
        subscription_types = []

        # Check if subscribed to publisher
        if (
            obj.publisher
            and hasattr(user, 'subscribed_publishers')
            and obj.publisher in user.subscribed_publishers.all()
        ):
            subscription_types.append('publisher')

        # Check if subscribed to journalist
        if (
            hasattr(user, 'subscribed_journalists')
            and obj.author in user.subscribed_journalists.all()
        ):
            subscription_types.append('journalist')

        return subscription_types if subscription_types else None


class JournalistSerializer(serializers.ModelSerializer):
    """
    Serializer for journalists (CustomUser with role='journalist').
    """
    full_name = serializers.SerializerMethodField()
    publishers = PublisherSerializer(many=True, read_only=True)
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'first_name', 'last_name', 'full_name',
            'email', 'publishers', 'article_count'
        ]
        read_only_fields = ['id', 'username', 'first_name', 'last_name',
                            'email']

    def get_full_name(self, obj):
        """Return the full name of the journalist."""
        return obj.get_full_name() or obj.username

    def get_article_count(self, obj):
        """Return the number of approved articles by this journalist."""
        return obj.authored_articles.filter(status='approved').count()
