
from django.core.management.base import BaseCommand, CommandError

from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware

from rivermap.utils import scrape_sections


def get_aware_datetime(date_str):
    print(date_str)
    ret = parse_datetime(date_str)
    if not is_aware(ret):
        ret = make_aware(ret)
    return ret


class Command(BaseCommand):
    help = 'Scrape water level of the rivers'

    def handle(self, *args, **options):
        scrape_sections()
