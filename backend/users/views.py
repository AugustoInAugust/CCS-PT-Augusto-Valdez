from rest_framework import viewsets

from accounts.permissions import IsAdminOrReadOnly
from users import services
from users.models import Person
from users.serializers import PersonSerializer


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['first_name', 'last_name', 'email', 'country']
    ordering_fields = ['id', 'first_name', 'last_name', 'email', 'country', 'birth_date']

    def perform_create(self, serializer):
        serializer.instance = services.create_person(
            serializer.validated_data, self.request.user
        )

    def perform_update(self, serializer):
        serializer.instance = services.update_person(
            serializer.instance, serializer.validated_data, self.request.user
        )

    def perform_destroy(self, instance):
        services.delete_person(instance, self.request.user)
