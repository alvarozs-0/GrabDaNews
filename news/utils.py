from .models import CustomUser, Publisher


def verify_username(username):
    if not username:
        return False
    if CustomUser.objects.filter(username=username).exists():
        return False
    return True


def verify_password(password):
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    return True


def verify_email(email):
    """Verify email format and uniqueness."""
    if not email or '@' not in email:
        return False
    if CustomUser.objects.filter(email=email).exists():
        return False
    return True


def verify_role_publisher(role, publisher_ids):
    """Verify role and publisher combination."""
    # Validate that all publisher IDs exist (if any are provided)
    if publisher_ids:
        for publisher_id in publisher_ids:
            try:
                Publisher.objects.get(id=publisher_id)
            except Publisher.DoesNotExist:
                return False, (f"Publisher with ID {publisher_id} does not "
                               f"exist.")
    return True, ""
