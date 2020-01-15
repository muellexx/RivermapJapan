import datetime, json
import sqlite3
from bs4 import BeautifulSoup as soup
from django.core.management.base import BaseCommand, CommandError
from urllib.request import urlopen as uReq

from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware

from rivermap.models import Observatory, Section


def get_aware_datetime(date_str):
    print(date_str)
    ret = parse_datetime(date_str)
    if not is_aware(ret):
        ret = make_aware(ret)
    return ret


class Command(BaseCommand):
    help = 'Scrape water level of the rivers'

    def handle(self, *args, **options):
        for observatory in Observatory.objects.all():
            # TODO multithread
            if observatory.section_set.count():
                url = observatory.url
                print(observatory.id)
                print(observatory.name)
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
                        print(str(datetime.datetime.today().year) + '-' + date.replace('/', '-') + 'T' + time.replace('24', '00') + ':00')
                        current_date_time = str(datetime.datetime.today().year) + '-' + date.replace('/', '-') + 'T' + time.replace('24', '00') + ':00'
                        print(current_date_time)
                    except ValueError:
                        pass

                    data['level'].append({
                        'date': date,
                        'time': time,
                        'level': level,
                    })

                with open(filename, 'w') as outfile:
                    json.dump(data, outfile, indent=4)

                print(current_date_time)
                print('hi')
                observatory.date = get_aware_datetime(current_date_time)
                observatory.level = current_level
                print(observatory.date)
                try:
                    observatory.date = get_aware_datetime(current_date_time)
                    observatory.level = current_level
                    observatory.save()
                except:
                    print("Error during observatory save")

        rivers = {'rivers': []}
        for section in Section.objects.all():
            rivers['rivers'].append({
                'id': section.id,
                'river': section.river.name,
                'name': section.name,
                #'url': section.observatory.url,
                #'level': section.observatory.level,
                #'date': observatory.date,
                'high_water': section.high_water,
                'middle_water': section.middle_water,
                'low_water': section.low_water,
                'start_lat': section.lat,
                'start_lng': section.lng,
                'end_lat': section.end_lat,
                'end_lng': section.end_lng,
            })
        with open('static/js/data/river.json', 'w') as outfile:
            json.dump(rivers, outfile, indent=4)
