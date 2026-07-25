from rest_framework.routers import DefaultRouter

from users.views import PersonViewSet

router = DefaultRouter()
router.register('users', PersonViewSet, basename='user')

urlpatterns = router.urls
