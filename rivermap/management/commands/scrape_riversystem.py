from bs4 import BeautifulSoup as soup
from django.core.management.base import BaseCommand
from urllib.request import urlopen as uReq
from urllib.error import HTTPError

from rivermap.models import River, Observatory, Dam, RiverSystem


class Command(BaseCommand):
    help = 'Scape the river systems of Japan'

    def handle(self, *args, **options):

        for observatory in Observatory.objects.all():
            if observatory.riversystem:
                continue
            print(observatory.id)
            try:
                url = observatory.url
                uClient = uReq(url)
                page_html = uClient.read()
                uClient.close()
                page_soup = soup(page_html, "html.parser")
                rivsys_name_jp = page_soup.find("div", {"class": "kobetuCntt"}).table.tr.td.table.find_all("tr")[1].td.text.strip()
                riv_name_jp = page_soup.find("div", {"class": "kobetuCntt"}).table.tr.td.table.find_all("tr")[1].find_all("td")[1].text.strip()

                if not RiverSystem.objects.filter(name_jp=rivsys_name_jp):
                    print("  rivsys " + rivsys_name_jp)
                    if not River.objects.filter(name_jp=rivsys_name_jp):
                        rivsys_name = "TODO"
                    else:
                        rivsys_name = River.objects.filter(name_jp=rivsys_name_jp)[0].name
                    print(rivsys_name)
                    riversystem = RiverSystem(name_jp=rivsys_name_jp, name=rivsys_name)
                    riversystem.save()
                else:
                    riversystem = RiverSystem.objects.filter(name_jp=rivsys_name_jp)[0]
                riversystem.prefecture.add(observatory.prefecture)
                riversystem.region.add(observatory.region)

                if River.objects.filter(name_jp=riv_name_jp):
                    river = River.objects.filter(name_jp=riv_name_jp)[0]
                    river.riversystem.add(riversystem)

                observatory.riversystem = riversystem
                observatory.save()
            except HTTPError:
                print("HTTPError")

        for dam in Dam.objects.all():
            if dam.riversystem:
                continue
            print(dam.id)
            try:
                url = dam.url
                uClient = uReq(url)
                page_html = uClient.read()
                uClient.close()
                page_soup = soup(page_html, "html.parser")
                rivsys_name_jp = page_soup.find("div", {"class": "kobetuCntt"}).table.tr.td.table.find_all("tr")[
                    1].td.text.strip()
                riv_name_jp = \
                page_soup.find("div", {"class": "kobetuCntt"}).table.tr.td.table.find_all("tr")[1].find_all("td")[
                    1].text.strip()

                if not RiverSystem.objects.filter(name_jp=rivsys_name_jp):
                    print("  rivsys " + rivsys_name_jp)
                    if not River.objects.filter(name_jp=rivsys_name_jp):
                        rivsys_name = "TODO"
                    else:
                        rivsys_name = River.objects.filter(name_jp=rivsys_name_jp)[0].name
                    print(rivsys_name)
                    riversystem = RiverSystem(name_jp=rivsys_name_jp, name=rivsys_name)
                    riversystem.save()
                else:
                    riversystem = RiverSystem.objects.filter(name_jp=rivsys_name_jp)[0]
                riversystem.prefecture.add(dam.prefecture)
                riversystem.region.add(dam.region)

                if River.objects.filter(name_jp=riv_name_jp):
                    river = River.objects.filter(name_jp=riv_name_jp)[0]
                    river.riversystem.add(riversystem)

                dam.riversystem = riversystem
                dam.save()
            except HTTPError:
                print("HTTPError")
