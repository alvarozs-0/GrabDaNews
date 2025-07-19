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


def verify_role_publisher(role, publisher_id):
    """Verify role and publisher combination."""
    if role in ['editor', 'journalist']:
        if not publisher_id:
            return False, "Editors and journalists must select a publisher."
        try:
            Publisher.objects.get(id=publisher_id)
            return True, ""
        except Publisher.DoesNotExist:
            return False, "Selected publisher does not exist."
    return True, ""
