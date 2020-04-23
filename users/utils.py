from django.utils import timezone

from users.models import ClientIP


def count_total():
    total = 0
    for ip in ClientIP.objects.all():
        if ip.admin:
            continue
        total = total + ip.count
    if ClientIP.objects.filter(ip='Total').exists():
        total_ip = ClientIP.objects.get(ip='Total')
        if total_ip.date_visited is None or timezone.now() - total_ip.date_visited > timezone.timedelta(seconds=100):
            total_ip.count = total
            total_ip.date_visited = timezone.now()
            total_ip.save()

