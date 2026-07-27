from datetime import date

import pytest

from accounts.models import Account
from users import services
from users.exceptions import PersonHasAccount
from users.models import Person

pytestmark = pytest.mark.django_db


@pytest.fixture
def actor():
    return Account.objects.get(username='admin')


def test_create_person_persists_the_record(actor):
    person = services.create_person(
        {
            'first_name': 'Created',
            'last_name': 'Directly',
            'email': 'created.directly@example.com',
            'phone': '+51 900 333 444',
            'country': 'Peru',
            'birth_date': date(1990, 1, 1),
        },
        actor,
    )

    assert person.pk is not None
    assert Person.objects.filter(email='created.directly@example.com').exists()


def test_update_person_applies_only_the_given_fields(person, actor):
    services.update_person(person, {'country': 'Chile'}, actor)

    person.refresh_from_db()
    assert person.country == 'Chile'
    assert person.first_name == 'Test'


def test_delete_person_removes_an_unlinked_record(person, actor):
    services.delete_person(person, actor)

    assert not Person.objects.filter(pk=person.pk).exists()


def test_delete_person_is_blocked_when_an_account_is_linked(actor):
    linked = Person.objects.get(email='admin@ccs.test')

    with pytest.raises(PersonHasAccount):
        services.delete_person(linked, actor)

    assert Person.objects.filter(pk=linked.pk).exists()
