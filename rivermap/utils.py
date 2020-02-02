import json

from django.utils import timezone

from rivermap.models import Section, MapObjectComment


def json_comments():
    comments = {'comments': []}
    for comment in MapObjectComment.objects.all():
        comments['comments'].append({
            'id': comment.id,
            'title': comment.title,
            'content': comment.content,
            'author': comment.author.username,
            'image_url': comment.author.profile.image.url,
            'date_posted': timezone.localtime(comment.date_posted).strftime('%Y/%m/%d %H:%M'),
        })
    with open('static/js/data/mapObjectComments.json', 'w') as outfile:
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
    with open('static/js/data/river.json', 'w') as outfile:
        json.dump(rivers, outfile, indent=4)
