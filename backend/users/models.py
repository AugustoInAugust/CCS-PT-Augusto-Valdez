from django.db import models


class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30)
    country = models.CharField(max_length=100)
    birth_date = models.DateField()

    class Meta:
        ordering = ['id']
        verbose_name = 'person'
        verbose_name_plural = 'people'

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
