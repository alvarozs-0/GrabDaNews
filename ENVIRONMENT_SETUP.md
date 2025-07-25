# Environment Setup Guide

## Environment Variables

This project uses environment variables to store sensitive configuration data. Follow these steps to set up your environment:

### 1. Create Environment File

Copy the example environment file and fill in your actual values:

```bash
cp .env.example .env
```

### 2. Configure Your Environment Variables

Edit the `.env` file and replace the placeholder values with your actual configuration:

#### Django Settings

- `SECRET_KEY`: Your Django secret key
- `DEBUG`: Set to `True` for development, `False` for production

#### Database Configuration

- `DB_ENGINE`: Database engine (default: `django.db.backends.mysql`) MariaDB was used.
- `DB_NAME`: Your database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host (default: `localhost`)
- `DB_PORT`: Database port (default: `3306`)

#### Twitter API Configuration

- `TWITTER_API_KEY`: Your Twitter API key
- `TWITTER_API_KEY_SECRET`: Your Twitter API key secret
- `TWITTER_ACCESS_TOKEN`: Your Twitter access token
- `TWITTER_ACCESS_TOKEN_SECRET`: Your Twitter access token secret

#### Social Media Settings

- `ENABLE_TWITTER_POSTING`: Set to `True` to enable Twitter integration, `False` to disable

### 3. Install Dependencies

Make sure to install the required packages:

```bash
pip install -r requirements.txt
```

### 4. Environment File Location

The `.env` file should be placed in the root directory of your Django project (same level as `manage.py`).

### 5. Generating a New Secret Key

To generate a new Django secret key, you can use:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 6. Database Information & Sample Data

#### Sample Data
The project includes sample data in `data.json` file which contains:
- Sample articles
- Test users with different roles (journalists, publishers, subscribers)
- Publisher information
- Article subscriptions

#### Superuser Access

**Superuser Credentials:**
- **Username:** `admin`
- **Password:** `password123`

You can use these credentials to:
- Access the Django admin interface at `/admin/`
- View all users and their roles
- Manage articles, publishers, and subscriptions
- Test the complete functionality of the application
