from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.contenttypes.models import ContentType


class Publisher(models.Model):
    """
    Django model representing a publisher organization.

    A publisher can have multiple editors and journalists associated with it.
    Readers can subscribe to publishers to receive notifications about
    new articles.

    :param str name: The unique name of the publisher
    :param str description: Description of the publisher
    """
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    """
    Extended Django user model with role-based functionality.

    Supports three user roles: reader, editor, and journalist, each with
    specific permissions and relationships to publishers and other users.

    :param str role: User role (reader, editor, or journalist)
    :param ManyToManyField subscribed_publishers: Publishers user subscribes to
    :param ManyToManyField subscribed_journalists: Journalists user follows
    :param ManyToManyField publishers: Publishers where user works (staff only)
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
        Override Django's save method to handle role-based assignments.

        Manages appropriate field clearing based on user role and automatically
        assigns users to correct permission groups.

        :param args: Positional arguments passed to parent save method
        :param kwargs: Keyword arguments passed to parent save method
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
        Assign user to the appropriate Django group based on their role.

        Removes user from existing groups and adds them to the role-specific
        group, creating the group if it doesn't exist.
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
        Configure permissions for a role-based group.

        Sets appropriate Django permissions for each user role type,
        controlling access to article creation, editing, and approval.

        :param Group group: Django group to configure permissions for
        :param str role: User role (reader, editor, or journalist)
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
    Django model representing a news article in the system.

    Articles have a submission and approval workflow, where journalists
    submit articles that must be approved by editors before publication.

    :param str title: Article headline/title
    :param str content: Full article text content
    :param CustomUser author: Journalist who wrote the article
    :param Publisher publisher: Publisher organization (optional)
    :param str status: Current review status (submitted/approved/rejected)
    :param datetime created_at: When article was first created
    :param datetime updated_at: Last modification timestamp
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
