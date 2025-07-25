Installation Guide
==================

This guide will help you set up the GrabDaNews Django application on your local development environment.

Prerequisites
-------------

* Python 3.8 or higher
* MySQL/MariaDB database server
* Git (for cloning the repository)

Environment Setup
-----------------

1. **Clone the Repository**

   .. code-block:: bash

      git clone https://github.com/alvarozs-0/GrabDaNews.git
      cd GrabDaNews

2. **Create Virtual Environment**

   .. code-block:: bash

      python -m venv .venv
      
      # On Windows (Git Bash)
      source .venv/Scripts/activate
      
      # On Windows (PowerShell)
      .venv\Scripts\Activate.ps1
      
      # On macOS/Linux
      source .venv/bin/activate

3. **Install Dependencies**

   .. code-block:: bash

      pip install -r requirements.txt

Environment Variables
--------------------

1. **Create Environment File**

   Copy the example environment file:

   .. code-block:: bash

      cp .env.example .env

2. **Configure Variables**

   Edit the `.env` file with your configuration:

   .. code-block:: bash

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

      # Twitter API Configuration (Optional)
      TWITTER_API_KEY=your-twitter-api-key
      TWITTER_API_KEY_SECRET=your-twitter-api-key-secret
      TWITTER_ACCESS_TOKEN=your-twitter-access-token
      TWITTER_ACCESS_TOKEN_SECRET=your-twitter-access-token-secret
      ENABLE_TWITTER_POSTING=True

Database Setup
--------------

1. **Create Database**

   Create a MySQL/MariaDB database for the project:

   .. code-block:: sql

      CREATE DATABASE grabdanews_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

2. **Run Migrations**

   .. code-block:: bash

      python manage.py migrate

3. **Load Sample Data (Optional)**

   .. code-block:: bash

      python manage.py loaddata data.json

4. **Create Superuser**

   .. code-block:: bash

      python manage.py createsuperuser

   Or use the default superuser:
   
   * **Username:** admin
   * **Password:** password123

Running the Application
-----------------------

1. **Start Development Server**

   .. code-block:: bash

      python manage.py runserver

2. **Access the Application**

   * **Main Site:** http://127.0.0.1:8000/
   * **Admin Interface:** http://127.0.0.1:8000/admin/
   * **API Root:** http://127.0.0.1:8000/api/

Testing
-------

Run the test suite:

.. code-block:: bash

   python manage.py test

Troubleshooting
---------------

**Common Issues:**

* **MySQL Connection Error:** Ensure MySQL/MariaDB is running and credentials are correct
* **Migration Errors:** Try ``python manage.py migrate --run-syncdb``
* **Missing Environment Variables:** Check your `.env` file configuration
* **Twitter Integration Issues:** Verify your Twitter API credentials
