from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Publisher, Article, Newsletter, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for CustomUser model.
    """
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {
            'fields': ('role', 'publishers')
        }),
        ('Subscriptions', {
            'fields': ('subscribed_publishers', 'subscribed_journalists')
        }),
    )

    list_display = (
        'username', 'email', 'role', 'get_publishers',
        'get_subscribed_publishers', 'get_subscribed_journalists', 'is_staff'
    )

    def get_subscribed_publishers(self, obj):
        """Display subscribed publishers for list view."""

        return ", ".join([pub.name for pub in obj.subscribed_publishers.all()])
    get_subscribed_publishers.short_description = 'Subscribed Publishers'

    def get_subscribed_journalists(self, obj):
        """Display subscribed journalists for list view."""

        return ", ".join([user.username for user in obj.subscribed_journalists.all()])
    get_subscribed_journalists.short_description = 'Subscribed Journalists'
    list_filter = ('role', 'publishers', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    def get_publishers(self, obj):
        """Display publishers for list view."""

        return ", ".join([pub.name for pub in obj.publishers.all()])
    get_publishers.short_description = 'Publishers'




@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """
    Admin configuration for Publisher model.
    """

    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Admin configuration for Article model.
    """
    list_display = (
        'title', 'author', 'publisher', 'status',
        'created_at'
    )
    list_filter = (
        'status', 'publisher', 'created_at'
    )
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Article Information', {
            'fields': ('title', 'content')
        }),
        ('Author & Publication', {
            'fields': ('author', 'publisher')
        }),
        ('Editorial', {
            'fields': ('status', 'approved_by')
        }),
        ('Publishing', {
            'fields': ('published_at',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    actions = ['approve_articles', 'reject_articles']

    def approve_articles(self, request, queryset):
        """
        Admin action to approve selected articles.
        """
        updated = queryset.update(
            status='approved',
            approved_by=request.user
        )
        self.message_user(
            request,
            f'{updated} articles were successfully approved.'
        )
    approve_articles.short_description = "Approve selected articles"

    def reject_articles(self, request, queryset):
        """
        Admin action to reject selected articles.
        """
        updated = queryset.update(
            status='rejected'
        )
        self.message_user(
            request,
            f'{updated} articles were successfully rejected.'
        )
    reject_articles.short_description = "Reject selected articles"


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """
    Admin configuration for Newsletter model.
    """
    list_display = ('title', 'author', 'publisher', 'status', 'created_at')
    list_filter = ('status', 'publisher', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Newsletter Information', {
            'fields': ('title', 'content')
        }),
        ('Author & Publication', {
            'fields': ('author', 'publisher')
        }),
        ('Status', {
            'fields': ('status', 'sent_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Subscription model.
    """
    list_display = (
        'subscriber', 'subscription_type', 'get_subscribed_to'
    )
    list_filter = ('subscription_type',)
    search_fields = (
        'subscriber__username', 'publisher__name',
        'journalist__username'
    )
    readonly_fields = ()

    def get_subscribed_to(self, obj):
        """
        Display what the user is subscribed to.
        """
        if obj.subscription_type == 'publisher':
            return obj.publisher.name if obj.publisher else 'N/A'
        else:
            return obj.journalist.username if obj.journalist else 'N/A'
    get_subscribed_to.short_description = 'Subscribed To'
