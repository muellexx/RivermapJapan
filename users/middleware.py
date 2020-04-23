from django.utils import timezone
from .models import Profile, ClientIP
from .utils import count_total


class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        assert hasattr(request, 'user'), 'The UpdateLastActivityMiddleware requires authentication middleware to be installed.'
        ip = request.META.get('REMOTE_ADDR')
        if ip:
            if ClientIP.objects.filter(ip=ip).exists():
                client_ip = ClientIP.objects.get(ip=ip)
                if timezone.now() - client_ip.date_visited > timezone.timedelta(seconds=600):
                    client_ip.date_visited = timezone.now()
                    client_ip.count = client_ip.count + 1
                    if not client_ip.user and request.user.is_authenticated:
                        client_ip.user = request.user
                    if request.user.is_superuser:
                        client_ip.admin = True
                    client_ip.save()
                    count_total()
            else:
                client_ip = ClientIP(ip=ip)
                if request.user.is_authenticated:
                    client_ip.user = request.user
                if request.user.is_superuser:
                    client_ip.admin = True
                client_ip.save()
                count_total()
        else:
            if ClientIP.objects.filter(ip='Unknown').exists():
                client_ip = ClientIP.objects.get(ip='Unknown')
                if timezone.now() - client_ip.date_visited > timezone.timedelta(seconds=600):
                    client_ip.date_visited = timezone.now()
                    client_ip.count = client_ip.count + 1
                    client_ip.save()
                    count_total()

        if request.user.is_authenticated and (request.user.profile.last_activity is None or timezone.now() -
                                              request.user.profile.last_activity > timezone.timedelta(seconds=300)):
            Profile.objects.filter(user__id=request.user.id).update(last_activity=timezone.now())
        response = self.get_response(request)
        return response
