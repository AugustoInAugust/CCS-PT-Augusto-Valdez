from datetime import date

from django.contrib.auth.hashers import make_password
from django.db import migrations

ACCOUNTS = [
    {
        'username': 'admin',
        'password': 'Admin123!',
        'role': 'ADMIN',
        'is_staff': True,
        'is_superuser': True,
        'person': {
            'first_name': 'System',
            'last_name': 'Administrator',
            'email': 'admin@ccs.test',
            'phone': '+51 900 000 001',
            'country': 'Peru',
            'birth_date': '1985-01-15',
        },
    },
    {
        'username': 'user123',
        'password': 'Password1!',
        'role': 'USER',
        'is_staff': False,
        'is_superuser': False,
        'person': {
            'first_name': 'Demo',
            'last_name': 'User',
            'email': 'user123@ccs.test',
            'phone': '+51 900 000 002',
            'country': 'Peru',
            'birth_date': '1995-06-20',
        },
    },
]


def create_accounts(apps, schema_editor):
    Person = apps.get_model('users', 'Person')
    Account = apps.get_model('accounts', 'Account')

    for entry in ACCOUNTS:
        person_data = dict(entry['person'])
        person_data['birth_date'] = date.fromisoformat(person_data['birth_date'])
        person = Person.objects.create(**person_data)

        Account.objects.create(
            username=entry['username'],
            password=make_password(entry['password']),
            role=entry['role'],
            is_staff=entry['is_staff'],
            is_superuser=entry['is_superuser'],
            is_active=True,
            person=person,
        )


def delete_accounts(apps, schema_editor):
    Person = apps.get_model('users', 'Person')
    Account = apps.get_model('accounts', 'Account')

    usernames = [entry['username'] for entry in ACCOUNTS]
    emails = [entry['person']['email'] for entry in ACCOUNTS]

    Account.objects.filter(username__in=usernames).delete()
    Person.objects.filter(email__in=emails).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('users', '0002_seed_people'),
    ]

    operations = [
        migrations.RunPython(create_accounts, delete_accounts),
    ]
