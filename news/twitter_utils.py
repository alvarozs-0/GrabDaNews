"""
Twitter/X integration for GrabDaNews
Automatically posts tweets when articles are approved
"""

from requests_oauthlib import OAuth1Session
from django.conf import settings

# Twitter API credentials
API_KEY = "pwHBMZjs7fd100AyYMFmGEpGm"
API_KEY_SECRET = "kBp4nbpgIyoHblpsEuXbKnQzUd2w6Cp3OopVHVLEkE7IFtEHDR"
ACCESS_TOKEN = "1879951288055570432-yD0vDxvnDaYCMDAIczBGrRUDBnKetC"
ACCESS_TOKEN_SECRET = "R7KHR739uiwvc4C4UyT75DjADPrRig691BMEuAkyHFV2L"


def send_tweet(text):
    """Send tweet using Twitter API v2 with OAuth 1.0a"""

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
    """Tweet when a news article is approved and published"""

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
