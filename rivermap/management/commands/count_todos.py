from bs4 import BeautifulSoup as soup
from django.core.management.base import BaseCommand, CommandError
from urllib.request import urlopen as uReq
from selenium import webdriver

from django.core.serializers import json
from googletrans import Translator
from rivermap.models import Prefecture, River, Observatory, Dam
import time


class Command(BaseCommand):
    help = 'Translate names of Rivers, Observatories and Dams to English'

    def handle(self, *args, **options):
        counter = 0
        rivers = River.objects.all()
        for river in rivers:
            if river.name == 'TODO':
                counter = counter + 1
        print(f"{counter} TODOs are left in Rivers")

        counter = 0
        observatories = Observatory.objects.all()
        for observatory in observatories:
            if observatory.name == 'TODO':
                counter = counter + 1
        print(f"{counter} TODOs are left in Observatories")

        counter = 0
        dams = Dam.objects.all()
        for dam in dams:
            if dam.name == 'TODO':
                counter = counter + 1
        print(f"{counter} TODOs are left in Dams")
