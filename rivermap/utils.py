import datetime
import json
import math
import re

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_aware

from RivermapJapan import settings
from rivermap.models import Section, MapObjectComment, Observatory, Spot, Dam


def calculate_distance(lat1, lng1, lat2, lng2):
    if lat1 == lat2 and lng1 == lng2:
        return 0
    radlat1 = math.pi * lat1 / 180
    radlat2 = math.pi * lat2 / 180
    theta = lng1 - lng2
    radtheta = math.pi * theta / 180
    dist = math.sin(radlat1) * math.sin(radlat2) + math.cos(radlat1) * math.cos(radlat2) * math.cos(radtheta);
    if dist > 1:
        dist = 1
    dist = math.acos(dist)
    dist = dist * 180 / math.pi
    dist = dist * 60 * 1.1515
    dist = dist * 1.609344
    return dist


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
    if not has_mw and has_lw and has_hw:
        mw = (hw + lw) / 2
        has_mw = True
    if has_hw and cl > hw:
        return 5
    if has_mw:
        if has_hw and cl > mw + 0.4 * (hw - mw):
            return 4
        elif has_hw and cl > mw:
            return 3
        elif cl > mw:
            if has_lw:
                if cl <= mw + 0.4 * (mw - lw):
                    return 3
                else:
                    return 5
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
    objects_to_scrape = ['obs', 'dam']
    for cycle in objects_to_scrape:
        if cycle == 'obs':
            observatories = Observatory.objects.all().filter(section__name__contains='') | \
                            Observatory.objects.all().filter(spot__name__contains='')
        elif cycle == 'dam':
            observatories = Dam.objects.all().filter(section__name__contains='') | \
                            Dam.objects.all().filter(spot__name__contains='')
        for observatory in observatories:
            # TODO multithread
            if (observatory.section_set.count() or observatory.spot_set.count()) and (
                    observatory.date is None or timezone.now() - observatory.date > timezone.timedelta(seconds=660)):
                write_json = True
                url = observatory.url
                if '&timeType=60' in url:
                    url = url.replace('&timeType=60', '&timeType=10')
                else:
                    url = url + "&timeType=10"
                uClient = uReq(url)
                page_html = uClient.read()
                uClient.close()

                # html parsing
                page_soup = soup(page_html, "html.parser")

                # get the table and the rows
                rows = page_soup.find("div", {"id": "hyou"}).table.find_all("tr")

                # Create and initialize file for result
                filename = 'static/js/data/river/' + cycle + '_' + str(observatory.id) + '.json'

                try:
                    with open(filename) as f:
                        data = json.load(f)
                    try:
                        latest_date_time = get_aware_datetime(str(datetime.datetime.today().year) + '-' + data['level'][-1]['date'].replace('/', '-') + \
                                       'T' + data['level'][-1]['time'] + ':00')
                    except AttributeError:
                        latest_date_time = observatory.date
                except (FileNotFoundError, IndexError) as e:
                    data = {'level': []}
                    latest_date_time = None

                date = '0'
                # loop through the rows of the table
                for row in rows:
                    cells = row.find_all("td")
                    time = cells[0].text.strip()
                    if len(time.split(' ')) > 1:
                        date = time.split(' ')[0]
                        time = time.split(' ')[1]
                    if cycle == 'obs':
                        level = cells[1].text.strip()
                    elif cycle == 'dam':
                        level = cells[3].text.strip()
                    try:
                        current_date_time = get_aware_datetime(str(datetime.datetime.today().year) + '-' + date.replace('/', '-') + 'T' +\
                                            time.replace('24', '00') + ':00')
                        if time == "24:00":
                            current_date_time += timezone.timedelta(days=1)
                            date = current_date_time.strftime('%m/%d')
                            time = "00:00"
                        level = float(level)
                        current_level = level
                        observatory.level = current_level
                    except ValueError:
                        current_level = None
                        pass
                    if latest_date_time and not latest_date_time < current_date_time:
                        continue

                    data['level'].append({
                        'date': date,
                        'time': time,
                        'level': level,
                    })

                if len(data['level']) > 1008:
                    data['level'] = data['level'][len(data['level'])-1008:]

                try:
                    with open(filename, 'w') as outfile:
                        json.dump(data, outfile, indent=4)
                except FileNotFoundError:
                    with open(settings.BASE_DIR + '/' + filename, 'w') as outfile:
                        json.dump(data, outfile, indent=4)

                try:
                    observatory.date = current_date_time
                    observatory.save()
                except:
                    print("Error during observatory save at observatory " + observatory.name)

    if write_json:
        json_sections()
        json_spots()
        json_comments()


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
                'date_posted': timezone.localtime(comment.date_posted).strftime('%Y/%m/%d'),
                'date_posted_jp': timezone.localtime(comment.date_posted).strftime('%Y年%m月%d日'),
            })
        if comment.image1:
            comments['comments'][-1]['image1'] = comment.image1.url
        if comment.image2:
            comments['comments'][-1]['image2'] = comment.image2.url
        if comment.image3:
            comments['comments'][-1]['image3'] = comment.image3.url
        if comment.image4:
            comments['comments'][-1]['image4'] = comment.image4.url
    try:
        with open('static/js/data/mapObjectComments.json', 'w') as outfile:
            json.dump(comments, outfile, indent=4)
    except FileNotFoundError:
        with open(settings.BASE_DIR+'/static/js/data/mapObjectComments.json', 'w') as outfile:
            json.dump(comments, outfile, indent=4)
    return comments['comments'][-1]


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
            'river_jp': section.river.name_jp,
            'river_id': section.river.id,
            'name': section.name,
            'name_jp': section.name_jp,
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
        if section.dam:
            color = get_color(section.dam.level, section.low_water, section.middle_water, section.high_water)
            rivers['rivers'][-1]['color'] = color
            rivers['rivers'][-1]['dam_name'] = section.dam.name
            rivers['rivers'][-1]['dam_name_jp'] = section.dam.name_jp
            rivers['rivers'][-1]['url'] = section.dam.url
            rivers['rivers'][-1]['dam_id'] = section.dam.id
            rivers['rivers'][-1]['level'] = section.dam.level
            rivers['rivers'][-1]['date'] = timezone.localtime(section.dam.date).strftime('%Y/%m/%d %H:%M')
            rivers['rivers'][-1]['date_jp'] = timezone.localtime(section.dam.date).strftime('%Y年%m月%d日 %H:%M')
        if section.observatory:
            color = get_color(section.observatory.level, section.low_water, section.middle_water, section.high_water)
            rivers['rivers'][-1]['observatory_name'] = section.observatory.name
            rivers['rivers'][-1]['observatory_name_jp'] = section.observatory.name_jp
            rivers['rivers'][-1]['observatory_id'] = section.observatory.id
            if not section.dam:
                rivers['rivers'][-1]['url'] = section.observatory.url
                rivers['rivers'][-1]['color'] = color
                rivers['rivers'][-1]['level'] = section.observatory.level
                rivers['rivers'][-1]['date'] = timezone.localtime(section.observatory.date).strftime('%Y/%m/%d %H:%M')
                rivers['rivers'][-1]['date_jp'] = timezone.localtime(section.observatory.date).strftime('%Y年%m月%d日 %H:%M')
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
            'river_jp': spot.river.name_jp,
            'river_id': spot.river.id,
            'name': spot.name,
            'name_jp': spot.name_jp,
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
        if spot.dam:
            color = get_color(spot.dam.level, spot.low_water, spot.middle_water, spot.high_water)
            spots['spots'][-1]['color'] = color
            spots['spots'][-1]['dam_name'] = spot.dam.name
            spots['spots'][-1]['dam_name_jp'] = spot.dam.name_jp
            spots['spots'][-1]['url'] = spot.dam.url
            spots['spots'][-1]['dam_id'] = spot.dam.id
            spots['spots'][-1]['level'] = spot.dam.level
            spots['spots'][-1]['date'] = timezone.localtime(spot.dam.date).strftime('%Y/%m/%d %H:%M')
            spots['spots'][-1]['date_jp'] = timezone.localtime(spot.dam.date).strftime('%Y年%m月%d日 %H:%M')
        if spot.observatory:
            color = get_color(spot.observatory.level, spot.low_water, spot.middle_water, spot.high_water)
            spots['spots'][-1]['observatory_name'] = spot.observatory.name
            spots['spots'][-1]['observatory_name_jp'] = spot.observatory.name_jp
            spots['spots'][-1]['observatory_id'] = spot.observatory.id
            if not spot.dam:
                spots['spots'][-1]['url'] = spot.observatory.url
                spots['spots'][-1]['color'] = color
                spots['spots'][-1]['level'] = spot.observatory.level
                spots['spots'][-1]['date'] = timezone.localtime(spot.observatory.date).strftime('%Y/%m/%d %H:%M')
                spots['spots'][-1]['date_jp'] = timezone.localtime(spot.observatory.date).strftime('%Y年%m月%d日 %H:%M')
    try:
        with open('static/js/data/spot.json', 'w') as outfile:
            json.dump(spots, outfile, indent=4)
    except FileNotFoundError:
        with open(settings.BASE_DIR+'/static/js/data/spot.json', 'w') as outfile:
            json.dump(spots, outfile, indent=4)


def fix_urls():
    for observatory in Dam.objects.all():
        url = observatory.url
        if '/pcfull/' in url:
            continue
        base = 'https://www.river.go.jp/kawabou/pcfull/'

        number = re.search('obsrvId=(.*)&gamenId', url).group(1)

        a = "tm?itmkndCd=" + number[7]
        b = "&ofcCd=" + number[0:5]
        c = "&obsCd=" + number[8:13]
        d = "&isCurrent=true&fld=0"

        nurl = base + a + b + c + d
        observatory.url = nurl
        observatory.save()

