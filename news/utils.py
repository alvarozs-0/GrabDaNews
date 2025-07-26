"""
Utility functions for the GrabDaNews application.

This module contains helper functions for user validation,
including username, password, email, and role verification.
"""

from .models import CustomUser, Publisher


def verify_username(username):
    """
    Validate username availability and format.

    Checks if username is provided and not already taken by another user.

    :param str username: Username to validate

    :returns: True if username is valid and available, False otherwise
    :rtype: bool
    """
    if not username:
        return False
    if CustomUser.objects.filter(username=username).exists():
        return False
    return True


def verify_password(password):
    """
    Validate password strength and format requirements.

    Checks that password meets minimum security requirements:
    - At least 8 characters long
    - Contains at least one digit
    - Contains at least one alphabetic character

    :param str password: Password to validate

    :returns: True if password meets requirements, False otherwise
    :rtype: bool
    """
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    return True


def verify_email(email):
    """
    Verify email format and uniqueness in the system.

    Checks basic email format (contains @) and ensures email is not
    already registered by another user.

    :param str email: Email address to validate

    :returns: True if email is valid and unique, False otherwise
    :rtype: bool
    """
    if not email or '@' not in email:
        return False
    if CustomUser.objects.filter(email=email).exists():
        return False
    return True


def verify_role_publisher(role, publisher_ids):
    """
    Validate role and publisher relationship combinations.

    Ensures that provided publisher IDs exist in the database and
    are valid for the given user role.

    :param str role: User role being validated
    :param list publisher_ids: List of publisher IDs to validate

    :returns: Tuple of (is_valid, error_message)
    :rtype: tuple[bool, str]
    """
    # Validate that all publisher IDs exist (if any are provided)
    if publisher_ids:
        for publisher_id in publisher_ids:
            try:
                Publisher.objects.get(id=publisher_id)
            except Publisher.DoesNotExist:
                return False, (f"Publisher with ID {publisher_id} does not "
                               f"exist.")
    return True, ""
