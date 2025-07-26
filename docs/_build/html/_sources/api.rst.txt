API Documentation
=================

GrabDaNews provides a RESTful API built with Django REST Framework for external integrations.

Authentication
--------------

The API uses session-based authentication. You need to be logged in to access most endpoints.

Base URL
--------

All API endpoints are prefixed with ``/api/``

Available Endpoints
-------------------

Articles
~~~~~~~~

**List Articles**

.. code-block:: http

   GET /api/articles/

Returns a list of all approved articles.


**Get Article Details**

.. code-block:: http

   GET /api/articles/{id}/

Returns detailed information about a specific approved article.

Publishers
~~~~~~~~~~

**List Publishers**

.. code-block:: http

   GET /api/publishers/

Returns a paginated list of all publishers ordered by name.

**Get Publisher Details**

.. code-block:: http

   GET /api/publishers/{id}/

Returns detailed information about a specific publisher.

**Get Publisher Articles**

.. code-block:: http

   GET /api/publishers/{id}/articles/

Returns a paginated list of approved articles published by a specific publisher.

Journalists
~~~~~~~~~~~

**List Journalists**

.. code-block:: http

   GET /api/journalists/

Returns a paginated list of all users with journalist role ordered by username.

**Get Journalist Details**

.. code-block:: http

   GET /api/journalists/{id}/

Returns detailed information about a specific journalist.

**Get Journalist Articles**

.. code-block:: http

   GET /api/journalists/{id}/articles/

Returns a paginated list of approved articles written by a specific journalist.

Subscription Feed
~~~~~~~~~~~~~~~~~

**Get Subscription Feed**

.. code-block:: http

   GET /api/subscription-feed/

Returns a personalized feed of articles from publishers and journalists the authenticated user subscribes to.

Authentication
~~~~~~~~~~~~~~

**Django REST Framework Auth**

.. code-block:: http

   GET /api/auth/

Provides Django REST Framework's browsable API authentication endpoints for development and testing.

Error Responses
---------------

The API returns standard HTTP status codes:

* **200**: Success
* **201**: Created
* **400**: Bad Request
* **401**: Unauthorized
* **403**: Forbidden
* **404**: Not Found
* **500**: Internal Server Error

Error responses include a message field:

.. code-block:: json

   {
     "error": "Error message description"
   }
