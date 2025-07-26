"""
Twitter/X integration module for GrabDaNews application.

This module provides functionality for automatically posting tweets when
articles are approved and published. It uses OAuth 1.0a authentication
with Twitter API v2.
"""

from requests_oauthlib import OAuth1Session
from django.conf import settings
from decouple import config

# Twitter API credentials
API_KEY = config('TWITTER_API_KEY')
API_KEY_SECRET = config('TWITTER_API_KEY_SECRET')
ACCESS_TOKEN = config('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = config('TWITTER_ACCESS_TOKEN_SECRET')


def send_tweet(text):
    """Send a tweet using Twitter API v2 with OAuth 1.0a authentication.

    :param str text: The text content of the tweet to be posted

    :returns: True if tweet was posted successfully, False otherwise
    :rtype: bool

    :raises Exception: If there's an error with the API request
    """

    url = "https://api.twitter.com/2/tweets"

    # Use OAuth 1.0a for v2 API (required for posting tweets)
    oauth = OAuth1Session(
        API_KEY,
        client_secret=API_KEY_SECRET,
        resource_owner_key=ACCESS_TOKEN,
        resource_owner_secret=ACCESS_TOKEN_SECRET,
    )

    payload = {"text": text}

    try:
        response = oauth.post(url, json=payload)
        if response.status_code == 201:
            print("Tweet sent successfully!")
            return True
        else:
            print(f"Error sending tweet: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error sending tweet: {e}")
        return False


def tweet_article_approved(article):
    """Post a tweet when a news article is approved and published.

    Creates a formatted tweet containing article title, author name, and
    publisher information. Handles text truncation to stay within Twitter's
    280 character limit.

    :param Article article: The Django model instance of the approved article

    :returns: True if tweet was posted successfully, False otherwise
    :rtype: bool
    """

    # Check if Twitter posting is enabled
    if not getattr(settings, 'ENABLE_TWITTER_POSTING', False):
        print("Twitter posting is disabled in settings")
        return False

    # Create tweet text with article info
    author_name = article.author.get_full_name() or article.author.username
    publisher_name = (article.publisher.name if article.publisher else
                      "Independent")

    # Truncate title if too long (Twitter has 280 character limit)
    max_title_length = 150  # Leave room for other text
    title = article.title
    if len(title) > max_title_length:
        title = title[:max_title_length-3] + "..."

    text = (
        f"New Article Published!\n\n"
        f"'{title}'\n\n"
        f"Author: {author_name}\n"
        f"Publisher: {publisher_name}\n\n"
        f"#GrabDaNews #Breaking #News"
    )

    # Ensure tweet doesn't exceed 280 characters
    if len(text) > 280:
        # Truncate title further if needed
        excess = len(text) - 280
        new_title_length = len(title) - excess - 3
        if new_title_length > 10:  # Keep at least 10 chars of title
            title = title[:new_title_length] + "..."
            text = (
                f"New Article Published!\n\n"
                f"'{title}'\n\n"
                f"Author: {author_name}\n"
                f"Publisher: {publisher_name}\n\n"
                f"#GrabDaNews #Breaking #News"
            )

    return send_tweet(text)
