from django.contrib import admin

from users.models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'country', 'phone']
    search_fields = ['first_name', 'last_name', 'email']
    list_filter = ['country']
    ordering = ['id']
