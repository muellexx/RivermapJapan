from bs4 import BeautifulSoup as soup
from django.core.management.base import BaseCommand, CommandError
from urllib.request import urlopen as uReq
from selenium import webdriver

from django.core.serializers import json
from googletrans import Translator
from rivermap.models import Prefecture, River, Observatory, Dam
import time


class Command(BaseCommand):
    help = 'Scape Info of all the rivers in Japan'

    def handle(self, *args, **options):
        translator = Translator()

        limit_reached = False

        rivers = River.objects.all()
        for river in rivers:
            if limit_reached:
                break
            if river.name == 'TODO':
                try:
                    river.name = translator.translate(river.name_jp, src='ja', dest='ja').pronunciation
                    if not river.name:
                        river.name = translator.translate(river.name_jp, src='ja', dest='en').text
                    if river.name.endswith("gawa"):
                        river.name = river.name.replace("gawa", " River")
                    elif river.name.endswith("kawa"):
                        river.name = river.name.replace("kawa", " River")
                    elif "River" not in river.name:
                        river.name = river.name + " River"
                    elif " River" not in river.name:
                        river.name.replace("River", " River")
                except ValueError:
                    limit_reached = True

        if limit_reached:
            print("Limit Reached!")
        else:
            print("Finished")
