"""
Essential test suite for the News API.
Covers core functionality with minimal, focused tests.
"""
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone

from .models import Article, Publisher, CustomUser


class BasicAPITest(APITestCase):
    """
    Essential API tests - just the basics for a busy developer.
    """

    def setUp(self):
        """Set up minimal test data."""

        self.client = APIClient()

        # Create test users
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='reader'
        )

        self.journalist = CustomUser.objects.create_user(
            username='journalist',
            email='journalist@example.com',
            password='testpass123',
            role='journalist'
        )

        # Create test publisher
        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            description='A test publisher'
        )

        # Create test article
        self.article = Article.objects.create(
            title='Test Article',
            content='This is test content.',
            author=self.journalist,
            publisher=self.publisher,
            status='approved',
            published_at=timezone.now()
        )

    def test_authentication_required(self):
        """Test that API endpoints require authentication."""

        endpoints = [
            reverse('news_api:article_list'),
            reverse('news_api:publisher_list'),
            reverse('news_api:journalist_list'),
        ]

        for endpoint in endpoints:
            response = self.client.get(endpoint)
            # DRF with IsAuthenticated can return 403 or 401
            # depending on authentication configuration
            self.assertIn(response.status_code,
                          [status.HTTP_401_UNAUTHORIZED,
                           status.HTTP_403_FORBIDDEN])

    def test_article_list_works(self):
        """Test article list with authentication."""

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('news_api:article_list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Article')

    def test_article_detail_works(self):
        """Test article detail endpoint."""

        self.client.force_authenticate(user=self.user)
        url = reverse('news_api:article_detail',
                      kwargs={'pk': self.article.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Article')

    def test_publisher_list_works(self):
        """Test publisher list endpoint."""

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('news_api:publisher_list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Publisher')

    def test_journalist_list_works(self):
        """Test journalist list endpoint."""

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('news_api:journalist_list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], 'journalist')

    def test_article_search_works(self):
        """Test article search functionality."""

        self.client.force_authenticate(user=self.user)
        url = reverse('news_api:article_list')
        response = self.client.get(url, {'search': 'Test'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_subscription_feed_works(self):
        """Test subscription feed endpoint."""

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('news_api:subscription_feed'))

        # Should work even with no subscriptions
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_404_handling(self):
        """Test 404 error handling."""

        self.client.force_authenticate(user=self.user)
        url = reverse('news_api:article_detail', kwargs={'pk': 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
