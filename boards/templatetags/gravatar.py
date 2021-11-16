import hashlib
from urllib.parse import urlencode

from django import template
from django.conf import settings

register = template.Library()

@register.filter
def gravatar(user):
    email = user.email.lower().encode('utf-8')
    default = "https://www.example.com/default.jpg" #ơ lsao để thay cái default này
    size = 256
    url = 'http://www.gravatar.com/avatar/{md5}?{params}'.format(
        md5 = hashlib.md5(email).hexdigest(),
        params = urlencode({'d': default, 's':str(size)})
    )
    return url