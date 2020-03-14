import datetime
import json

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_aware

from RivermapJapan import settings
from rivermap.models import Section, MapObjectComment, Observatory, Spot


def get_aware_datetime(date_str):
    ret = parse_datetime(date_str)
    if not is_aware(ret):
        ret = make_aware(ret)
    return ret


def get_color(cl, lw, mw, hw):
    if not cl and not cl == 0:
        return 0
    has_lw = lw or lw == 0
    has_mw = mw or mw == 0
    has_hw = hw or hw == 0
    if has_hw and cl > hw:
        return 5
    if has_mw:
        if has_hw and cl > mw + 0.4 * (hw - mw):
            return 4
        elif has_hw and cl > mw:
            return 3
        elif cl > mw:
            if has_lw and cl <= + 0.4 * (mw - lw):
                return 3
            else:
                return 0
        if has_hw and not has_lw and cl > mw - 0.4 * (hw - mw):
            return 3
    if has_lw:
        if has_mw and cl > mw - 0.4 * (mw - lw):
            return 3
        elif has_mw and cl > lw:
            return 2
        elif cl > lw:
            return 0
        else:
            return 1
    return 0


def scrape_sections():
    write_json = False
    observatories = Observatory.objects.all().filter(section__name__contains='') | \
                    Observatory.objects.all().filter(spot__name__contains='')
    for observatory in observatories:
        # TODO multithread
        if (observatory.section_set.count() or observatory.spot_set.count()) and (
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
                    current_date_time = str(datetime.datetime.today().year) + '-' + date.replace('/', '-') + 'T' +\
                                        time.replace('24', '00') + ':00'
                    current_level = level
                except ValueError:
                    current_level = None
                    pass

                data['level'].append({
                    'date': date,
                    'time': time,
                    'level': level,
                })

            try:
                with open('static/js/data/river/' + str(observatory.id) + '.json', 'w') as outfile:
                    json.dump(data, outfile, indent=4)
            except FileNotFoundError:
                with open(settings.BASE_DIR + '/static/js/data/river/' + str(observatory.id) + '.json', 'w') as outfile:
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
        json_spots()


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
        color = 0
        rivers['rivers'].append({
            'id': section.id,
            'river': section.river.name,
            'river_id': section.river.id,
            'name': section.name,
            'prefecture': section.prefecture.name,
            'color': color,
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
        if section.observatory:
            color = get_color(section.observatory.level, section.low_water, section.middle_water, section.high_water)
            rivers['rivers'][-1]['color'] = color
            rivers['rivers'][-1]['observatory_name'] = section.observatory.name
            rivers['rivers'][-1]['url'] = section.observatory.url
            rivers['rivers'][-1]['observatory_id'] = section.observatory.id
            rivers['rivers'][-1]['level'] = section.observatory.level
            rivers['rivers'][-1]['date'] = timezone.localtime(section.observatory.date).strftime('%Y/%m/%d %H:%M')
    try:
        with open('static/js/data/river.json', 'w') as outfile:
            json.dump(rivers, outfile, indent=4)
    except FileNotFoundError:
        with open(settings.BASE_DIR+'/static/js/data/river.json', 'w') as outfile:
            json.dump(rivers, outfile, indent=4)


def json_spots():
    spots = {'spots': []}
    for spot in Spot.objects.all():
        comments = []
        for comment in spot.mapobjectcomment_set.all().order_by('date_posted'):
            comments.append(comment.id)
        color = 0
        spots['spots'].append({
            'id': spot.id,
            'river': spot.river.name,
            'river_id': spot.river.id,
            'name': spot.name,
            'prefecture': spot.prefecture.name,
            'color': color,
            'content': spot.content,
            'difficulty': spot.difficulty,
            'high_water': spot.high_water,
            'middle_water': spot.middle_water,
            'low_water': spot.low_water,
            'lat': spot.lat,
            'lng': spot.lng,
            'comments': comments,
        })
        if spot.observatory:
            color = get_color(spot.observatory.level, spot.low_water, spot.middle_water, spot.high_water)
            spots['spots'][-1]['color'] = color
            spots['spots'][-1]['observatory_name'] = spot.observatory.name
            spots['spots'][-1]['url'] = spot.observatory.url
            spots['spots'][-1]['observatory_id'] = spot.observatory.id
            spots['spots'][-1]['level'] = spot.observatory.level
            spots['spots'][-1]['date'] = timezone.localtime(spot.observatory.date).strftime('%Y/%m/%d %H:%M')
    try:
        with open('static/js/data/spot.json', 'w') as outfile:
            json.dump(spots, outfile, indent=4)
    except FileNotFoundError:
        with open(settings.BASE_DIR+'/static/js/data/spot.json', 'w') as outfile:
            json.dump(spots, outfile, indent=4)
