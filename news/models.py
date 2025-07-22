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
        except ContentType.DoesNotExist:
            # Content types not created yet during migrations
            return

        if role == 'reader':
            # Readers can only view articles
            permissions = [
                'view_article',
            ]
        elif role == 'editor':
            # Editors can view, update, and delete articles
            permissions = [
                'view_article',
                'change_article',
                'delete_article',
            ]
        elif role == 'journalist':
            # Journalists can create, view, update, and delete articles
            permissions = [
                'add_article',
                'view_article',
                'change_article',
                'delete_article',
            ]

        # Add permissions to group
        for perm_codename in permissions:
            try:
                permission = Permission.objects.get(
                    codename=perm_codename,
                    content_type=article_ct
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
        # Only auto-set publisher if this is a new article (no ID yet)
        # and no publisher is explicitly set
        if (not self.pk and
                not self.publisher and
                self.author.publishers.exists()):
            # Check if this is explicitly meant to be independent
            force_independent = kwargs.pop('force_independent', False)
            if not force_independent:
                self.publisher = self.author.publishers.first()
        else:
            # Remove the flag if it exists (for subsequent saves)
            kwargs.pop('force_independent', None)

        super().save(*args, **kwargs)
