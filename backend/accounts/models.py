from django.contrib.auth.models import AbstractUser
from django.db import models


class Account(AbstractUser):
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        USER = 'USER', 'User'

    person = models.OneToOneField(
        'users.Person',
        on_delete=models.PROTECT,
        related_name='account',
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )

    REQUIRED_FIELDS = ['person']

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
