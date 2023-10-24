from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

class User(AbstractUser):
    USER_TYPES = [
        ('expert', _('Confident')),
        ('intermediate', _('Less confident')),
        ('non-expert', _('Not confident'))
    ]
    user_type = models.CharField(
        max_length=30,
        choices=USER_TYPES,
        default='non-expert',
    )
