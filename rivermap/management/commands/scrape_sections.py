import datetime, json
import sqlite3
from bs4 import BeautifulSoup as soup
from django.core.management.base import BaseCommand, CommandError
from urllib.request import urlopen as uReq

from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware

from rivermap.models import Observatory, Section
from rivermap.utils import json_sections


def get_aware_datetime(date_str):
    print(date_str)
    ret = parse_datetime(date_str)
    if not is_aware(ret):
        ret = make_aware(ret)
    return ret


class Command(BaseCommand):
    help = 'Scrape water level of the rivers'

    def handle(self, *args, **options):
        write_json = False
        for observatory in Observatory.objects.all().filter(section__name__contains=''):
            # TODO multithread
            if observatory.section_set.count() and (
                    observatory.date is None or timezone.now() - observatory.date > timezone.timedelta(seconds=3600)):
                write_json = True
                url = observatory.url
                print(f'scrape {observatory}, id {observatory.id}')
                uClient = uReq(url)
                page_html = uClient.read()
                uClient.close()

                # html parsing
                page_soup = soup(page_html, "html.parser")

                # get the table and the rows
                rows = page_soup.find("div", {"id": "hyou"}).table.find_all("tr")

                # Create and initialize file for result
                filename = 'static/js/data/river/' + str(observatory.id) + '.json'

                data = {'level': []}

                date = '0'
                # loop through the rows of the table
                for row in rows:
                    cells = row.find_all("td")
                    time = cells[0].text.strip()
                    if len(time.split(' ')) > 1:
                        date = time.split(' ')[0]
                        time = time.split(' ')[1]
                    level = cells[1].text.strip()
                    try:
                        level = float(level)
                        current_level = level
                        current_date_time = str(datetime.datetime.today().year) + '-' + date.replace('/', '-') + 'T' + time.replace('24', '00') + ':00'
                    except ValueError:
                        pass

                    data['level'].append({
                        'date': date,
                        'time': time,
                        'level': level,
                    })

                with open(filename, 'w') as outfile:
                    json.dump(data, outfile, indent=4)

                observatory.level = current_level
                try:
                    observatory.date = get_aware_datetime(current_date_time)
                    observatory.level = current_level
                    observatory.save()
                    print('saved River ' + observatory.name)
                except:
                    print("Error during observatory save at observatory " + observatory.name)

        if write_json:
            json_sections()
