import logging

from users.exceptions import PersonHasAccount
from users.models import Person

logger = logging.getLogger(__name__)


def create_person(data, actor):
    person = Person.objects.create(**data)
    logger.info('Person %s created by %r', person.id, actor.username)
    return person


def update_person(person, data, actor):
    for field, value in data.items():
        setattr(person, field, value)
    person.save()
    logger.info('Person %s updated by %r', person.id, actor.username)
    return person


def delete_person(person, actor):
    if hasattr(person, 'account'):
        logger.warning(
            'Person %s could not be deleted by %r: a login account is linked to it',
            person.id,
            actor.username,
        )
        raise PersonHasAccount()

    person_id = person.id
    person.delete()
    logger.info('Person %s deleted by %r', person_id, actor.username)
