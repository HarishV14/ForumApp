import hashlib
from urllib.parse import urlencode
from django import template

register = template.Library()

@register.filter
def gravatar(user, size=50):
    """Returns a Gravatar URL for the given user."""
    email_hash = hashlib.md5(user.email.lower().encode('utf-8')).hexdigest()
    params = urlencode({'d': 'mm', 's': str(size)})
    return f"https://www.gravatar.com/avatar/{email_hash}?{params}"
