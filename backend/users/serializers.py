from datetime import date

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import Person


class PersonSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=Person.objects.all(),
                message='A person with this email already exists.',
            )
        ]
    )

    class Meta:
        model = Person
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone',
            'country',
            'birth_date',
        ]
        read_only_fields = ['id']

    def validate_birth_date(self, value):
        if value > date.today():
            raise serializers.ValidationError('Birth date cannot be in the future.')
        return value
