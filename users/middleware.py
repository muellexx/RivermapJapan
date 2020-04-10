from django.utils import timezone
from .models import Profile


class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        assert hasattr(request, 'user'), 'The UpdateLastActivityMiddleware requires authentication middleware to be installed.'
        if request.user.is_authenticated and (request.user.profile.last_activity is None or timezone.now() -
                                              request.user.profile.last_activity > timezone.timedelta(seconds=300)):
            Profile.objects.filter(user__id=request.user.id).update(last_activity=timezone.now())
        response = self.get_response(request)
        return response
