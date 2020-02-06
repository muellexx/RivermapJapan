import datetime
import json

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_aware

from RivermapJapan import settings
from rivermap.models import Section, MapObjectComment, Observatory


def get_aware_datetime(date_str):
    ret = parse_datetime(date_str)
    if not is_aware(ret):
        ret = make_aware(ret)
    return ret


def scrape_sections():
    write_json = False
    for observatory in Observatory.objects.all().filter(section__name__contains=''):
        # TODO multithread
        if observatory.section_set.count() and (
                observatory.date is None or timezone.now() - observatory.date > timezone.timedelta(seconds=3600)):
            write_json = True
            url = observatory.url
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
                    current_date_time = str(datetime.datetime.today().year) + '-' + date.replace('/',
                                                                                                 '-') + 'T' + time.replace(
                        '24', '00') + ':00'
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
            except:
                print("Error during observatory save at observatory " + observatory.name)

    if write_json:
        json_sections()


def json_comments():
    comments = {'comments': []}
    for comment in MapObjectComment.objects.all():
        if not comment.author:
            comments['comments'].append({
                'id': comment.id,
                'title': comment.title,
                'content': comment.content,
                'author': "Deleted User",
                'image_url': "/media/default.jpg",
                'date_posted': timezone.localtime(comment.date_posted).strftime('%Y/%m/%d %H:%M'),
            })
        else:
            comments['comments'].append({
                'id': comment.id,
                'title': comment.title,
                'content': comment.content,
                'author': comment.author.username,
                'image_url': comment.author.profile.image.url,
                'date_posted': timezone.localtime(comment.date_posted).strftime('%Y/%m/%d %H:%M'),
            })
    try:
        with open('static/js/data/mapObjectComments.json', 'w') as outfile:
            json.dump(comments, outfile, indent=4)
    except FileNotFoundError:
        with open(settings.BASE_DIR+'/static/js/data/mapObjectComments.json', 'w') as outfile:
            json.dump(comments, outfile, indent=4)


def json_sections():
    rivers = {'rivers': []}
    for section in Section.objects.all():
        comments = []
        for comment in section.mapobjectcomment_set.all().order_by('date_posted'):
            comments.append(comment.id)
        if section.observatory:
            rivers['rivers'].append({
                'id': section.id,
                'river': section.river.name,
                'river_id': section.river.id,
                'name': section.name,
                'prefecture': section.prefecture.name,
                'content': section.content,
                'difficulty': section.difficulty,
                'observatory_name': section.observatory.name,
                'url': section.observatory.url,
                'observatory_id': section.observatory.id,
                'level': section.observatory.level,
                'date': timezone.localtime(section.observatory.date).strftime('%Y/%m/%d %H:%M'),
                'high_water': section.high_water,
                'middle_water': section.middle_water,
                'low_water': section.low_water,
                'start_lat': section.lat,
                'start_lng': section.lng,
                'end_lat': section.end_lat,
                'end_lng': section.end_lng,
                'comments': comments,
            })
        else:
            rivers['rivers'].append({
                'id': section.id,
                'river': section.river.name,
                'river_id': section.river.id,
                'name': section.name,
                'prefecture': section.prefecture.name,
                'content': section.content,
                'difficulty': section.difficulty,
                'high_water': section.high_water,
                'middle_water': section.middle_water,
                'low_water': section.low_water,
                'start_lat': section.lat,
                'start_lng': section.lng,
                'end_lat': section.end_lat,
                'end_lng': section.end_lng,
                'comments': comments,
            })
    try:
        with open('static/js/data/river.json', 'w') as outfile:
            json.dump(rivers, outfile, indent=4)
    except FileNotFoundError:
        with open(settings.BASE_DIR+'/static/js/data/river.json', 'w') as outfile:
            json.dump(rivers, outfile, indent=4)

