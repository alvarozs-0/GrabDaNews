# GrabDaNews

A Django-based news management platform that allows publishers, editors, and journalists to collaborate on article creation, review, and publishing with Twitter/X integration.

## Features

- **User Management**: Custom user model with roles (Publisher, Editor, Journalist)
- **Article Management**: Create, edit, review, and publish articles
- **Subscription System**: Users can subscribe to publishers
- **Twitter/X Integration**: Automatic posting to social media
- **REST API**: Full API endpoints for all functionality
- **Responsive UI**: Bootstrap-styled templates

## Prerequisites

- Python 3.10+ (Python 3.13.5 recommended)
- pip (Python package manager)
- Docker (For containerized deployment)
- Git

## Installation & Setup

### 1: Virtual Environment Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/alvarozs-0/GrabDaNews.git
   cd GrabDaNews
   ```

2. **Create and activate virtual environment**

   ```bash
   # Windows
   python -m venv venv
   source venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment configuration file**

   Create a `.env` file in the project root directory:

   ```bash
   # Django Settings
   SECRET_KEY=your-secret-key-here
   DEBUG=True

   # Database Configuration
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=your-database-name
   DB_USER=your-database-user
   DB_PASSWORD=your-database-password
   DB_HOST=localhost
   DB_PORT=3306

   # Twitter API Configuration
   TWITTER_API_KEY=your-twitter-api-key
   TWITTER_API_KEY_SECRET=your-twitter-api-key-secret
   TWITTER_ACCESS_TOKEN=your-twitter-access-token
   TWITTER_ACCESS_TOKEN_SECRET=your-twitter-access-token-secret

   # Social Media Settings
   ENABLE_TWITTER_POSTING=True
   ```

5. **Set up initial data**

   You can either create your own data from scratch, or load sample data from `data.json`:

   - **To load sample data (includes a superuser):**

     ```bash
     python manage.py loaddata data.json
     ```

     The sample data includes a superuser:

     - **Username:** `admin`
     - **Password:** `password123`

     All users in the sample data have the password `password123`. You can log in as `admin` to view and manage the data.

   - **Or, create your own data:**
     1. **Run database migrations**
        ```bash
        python manage.py migrate
        ```
     2. **Create a superuser (optional)**
        ```bash
        python manage.py createsuperuser
        ```

6. **Run the development server**

   ```bash
   python manage.py runserver
   ```

   The application will be available at: http://localhost:8000

### Docker Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/alvarozs-0/GrabDaNews.git
   cd GrabDaNews
   ```

2. **Build the Docker image**

   ```bash
   docker build -t grabdanews .
   ```

3. **Run the container**

   ```bash
   # Basic run (SQLite database)
   docker run -d -p 8000:8000 grabdanews
   ```

   The application will be available at: http://localhost:8000

4. **Or run my image from Docker Hub in Docker Playground**

   ```bash
   docker run -d -b 8000:8000 alvarozs0/grabdanews
   ```

   Open on port 8000

   The sample data includes a superuser:

     - **Username:** `admin`
     - **Password:** `password123`

     All users in the sample data have the password `password123`. You can log in as `admin` to view and manage the data.
