from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.contenttypes.models import ContentType


class Publisher(models.Model):
    """
    Model representing a news publication/publisher.
    A publisher can have multiple editors and journalists.
    """
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    """
    Custom user model with roles and specific fields for different user types.
    """
    ROLE_CHOICES = [
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='reader'
    )

    # Fields for Reader role
    subscribed_publishers = models.ManyToManyField(
        Publisher,
        blank=True,
        related_name='subscribers'
    )

    subscribed_journalists = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        limit_choices_to={'role': 'journalist'},
        related_name='journalist_subscribers'
    )

    # Fields for Editor/Journalist roles
    publishers = models.ManyToManyField(
        Publisher,
        blank=True,
        related_name='staff_members'
    )

    def save(self, *args, **kwargs):
        """
        Override save method to handle role-based field assignments
        and group membership.
        """
        # Clear inappropriate fields based on role
        if self.role == 'journalist':
            # Journalists can't subscribe to others
            pass  # We'll handle this in post_save signal
        elif self.role in ['editor', 'reader']:
            # Editors and readers don't publish independently
            pass

        super().save(*args, **kwargs)

        # Assign user to appropriate group based on role
        self.assign_to_group()

    def assign_to_group(self):
        """
        Assign user to appropriate group based on their role.
        """
        # Remove user from all existing groups
        self.groups.clear()

        # Add user to appropriate group
        group_name = f"{self.role.capitalize()}s"
        group, created = Group.objects.get_or_create(name=group_name)
        self.groups.add(group)

        # Set permissions for the group if it was just created
        if created:
            self.set_group_permissions(group, self.role)

    def set_group_permissions(self, group, role):
        """
        Set permissions for groups based on role.
        """
        # Get content types for our models
        try:
            article_ct = ContentType.objects.get(
                app_label='news',
                model='article'
            )
            newsletter_ct = ContentType.objects.get(
                app_label='news',
                model='newsletter'
            )
        except ContentType.DoesNotExist:
            # Content types not created yet during migrations
            return

        if role == 'reader':
            # Readers can only view articles and newsletters
            permissions = [
                'view_article',
                'view_newsletter',
            ]
        elif role == 'editor':
            # Editors can view, update, and delete articles and newsletters
            permissions = [
                'view_article',
                'change_article',
                'delete_article',
                'view_newsletter',
                'change_newsletter',
                'delete_newsletter',
            ]
        elif role == 'journalist':
            # Journalists can create, view, update, and delete
            # articles and newsletters
            permissions = [
                'add_article',
                'view_article',
                'change_article',
                'delete_article',
                'add_newsletter',
                'view_newsletter',
                'change_newsletter',
                'delete_newsletter',
            ]

        # Add permissions to group
        for perm_codename in permissions:
            try:
                if 'article' in perm_codename:
                    permission = Permission.objects.get(
                        codename=perm_codename,
                        content_type=article_ct
                    )
                else:
                    permission = Permission.objects.get(
                        codename=perm_codename,
                        content_type=newsletter_ct
                    )
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                pass  # Permission will be created after migrations

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        ordering = ['username']


class Article(models.Model):
    """
    Model representing a news article.
    """
    STATUS_CHOICES = [
        ('submitted', 'Submitted for Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()

    # Author information
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'journalist'},
        related_name='authored_articles'
    )

    # Publication information
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='articles',
        null=True,
        blank=True
    )

    # Editorial workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted'
    )
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'editor'},
        related_name='approved_articles'
    )

    # Publishing details
    published_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('can_approve_article', 'Can approve articles'),
            ('can_publish_article', 'Can publish articles'),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Override save to handle approval workflow.
        """
        # Auto-set publisher based on author's publisher if not set
        if not self.publisher and self.author.publisher:
            self.publisher = self.author.publisher

        super().save(*args, **kwargs)


class Newsletter(models.Model):
    """
    Model representing a newsletter.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()

    # Author information
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['journalist', 'editor']},
        related_name='authored_newsletters'
    )

    # Publication information
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='newsletters',
        null=True,
        blank=True
    )

    # Newsletter details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Override save to handle publisher assignment.
        """
        # Auto-set publisher based on author's publisher if not set
        if not self.publisher and self.author.publisher:
            self.publisher = self.author.publisher

        super().save(*args, **kwargs)


class Subscription(models.Model):
    """
    Model to track user subscriptions to publishers and journalists.
    """
    SUBSCRIPTION_TYPES = [
        ('publisher', 'Publisher'),
        ('journalist', 'Journalist'),
    ]

    subscriber = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )

    subscription_type = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_TYPES
    )

    # Foreign keys to subscribed entities
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subscriptions'
    )
    journalist = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={'role': 'journalist'},
        related_name='journalist_subscriptions'
    )

    class Meta:
        unique_together = [
            ('subscriber', 'publisher'),
            ('subscriber', 'journalist'),
        ]

    def __str__(self):
        if self.subscription_type == 'publisher':
            return f"{self.subscriber.username} -> {self.publisher.name}"
        else:
            return f"{self.subscriber.username} -> {self.journalist.username}"
