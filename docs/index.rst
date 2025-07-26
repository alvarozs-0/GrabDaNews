.. GrabDaNews documentation master file, created by
   sphinx-quickstart on Fri Jul 25 15:54:17 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GrabDaNews Documentation
========================

Welcome to GrabDaNews, a Django-based news management system that allows 
journalists to submit articles, editors to approve them, and readers to 
subscribe to their favorite publishers and journalists.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   modules
   api

Features
--------

* **Multi-role System**: Support for journalists, editors, and readers
* **Article Management**: Complete workflow from submission to publication
* **Subscription System**: Users can subscribe to publishers and journalists
* **Twitter Integration**: Automatic tweet posting when articles are approved
* **Email Notifications**: Subscribers receive email alerts for new articles
* **RESTful API**: Complete API for external integrations

Quick Start
-----------

1. Set up your environment variables using the `.env.example` file
2. Install dependencies: ``pip install -r requirements.txt``
3. Run migrations: ``python manage.py migrate``
4. Create a superuser: ``python manage.py createsuperuser``
5. Start the development server: ``python manage.py runserver``

User Roles
----------

**Journalists**
   Can create and submit articles for review

**Editors** 
   Can approve or reject submitted articles

**Readers**
   Can view published articles and subscribe to publishers/journalists

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

