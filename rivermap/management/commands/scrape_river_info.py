import json
import sqlite3
from bs4 import BeautifulSoup as soup
from django.core.management.base import BaseCommand, CommandError
from urllib.request import urlopen as uReq
from googletrans import Translator
from rivermap.models import Prefecture, River, Observatory, Dam


class Command(BaseCommand):
    help = 'Scape Info of all the rivers in Japan'

    def handle(self, *args, **options):
        translator = Translator()

        prefecture = Prefecture.objects.all()[0]
        region = prefecture.region

        url = 'http://www.river.go.jp/kawabou/ipGaikyoMap.do?areaCd=81&prefCd=0102&townCd=&gamenId=01-0704&fldCtlParty=no'
        uClient = uReq(url)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")
        observatory_url = "http://www.river.go.jp" + page_soup.find("div", {"class": "obsdata-box"}).find_all('a')[1].\
            get('href')
        dam_url = "http://www.river.go.jp" + page_soup.find("div", {"class": "obsdata-box"}).find_all('a')[2].\
            get('href')

        uClient = uReq(observatory_url)
        sub_page_html = uClient.read()
        uClient.close()
        sub_page_soup = soup(sub_page_html, "html.parser")
        rows = sub_page_soup.find("div", {"class": "gaikyoCntt"}).table.find_all("tr")[2:]

        for row in rows:

            col = row.find_all("td")[2]
            riv_name_jp = col.text.strip()
            if riv_name_jp == 'その他':
                continue

            if not River.objects.filter(name_jp=riv_name_jp):
                riv_name = translator.translate(riv_name_jp, src='ja', dest='ja').pronunciation
                if not riv_name:
                    riv_name = translator.translate(riv_name_jp, src='ja', dest='en').text
                if "gawa" in riv_name:
                    riv_name = riv_name.replace("gawa", " River")
                if "kawa" in riv_name:
                    riv_name = riv_name.replace("kawa", " River")
                else:
                    riv_name = riv_name + " River"
                river = River(name_jp=riv_name_jp, name=riv_name)
                river.save()
            else:
                river = River.objects.filter(name_jp=riv_name_jp)[0]

            river.prefecture.add(prefecture)
            river.region.add(region)

            col = row.find_all("td")[0]
            obs_url = ("http://www.river.go.jp/kawabou/ipSuiiKobetu.do?obsrvId=" +
                       col.a.get('href').split("'")[3] +
                       "&gamenId=01-1003&stgGrpKind=survForeKjExpl&fldCtlParty=no&fvrt=yes")
            if not Observatory.objects.filter(url=obs_url):
                obs_name_jp = col.a.text.strip()
                obs_name = translator.translate(obs_name_jp, src='ja', dest='ja').pronunciation
                if not obs_name:
                    obs_name = translator.translate(obs_name_jp, src='ja', dest='en').text
                observatory = Observatory(name_jp=obs_name_jp, name=obs_name, url=obs_url)
                observatory.save()
            else:
                observatory = Observatory.objects.filter(url=obs_url)[0]

            observatory.river.add(river)

        uClient = uReq(dam_url)
        sub_page_html = uClient.read()
        uClient.close()
        sub_page_soup = soup(sub_page_html, "html.parser")
        rows = sub_page_soup.find("div", {"class": "gaikyoCntt"}).table.find_all("tr")[1:]
        for row in rows:

            col = row.find_all("td")[2]
            riv_name_jp = col.text.strip()
            if riv_name_jp == 'その他':
                continue

            if not River.objects.filter(name_jp=riv_name_jp):
                riv_name = translator.translate(riv_name_jp, src='ja', dest='ja').pronunciation
                if not riv_name:
                    riv_name = translator.translate(riv_name_jp, src='ja', dest='en').text
                if "gawa" in riv_name:
                    riv_name = riv_name.replace("gawa", " River")
                elif "kawa" in riv_name:
                    riv_name = riv_name.replace("kawa", " River")
                else:
                    riv_name = riv_name + " River"

                river = River(name_jp=riv_name_jp, name=riv_name)
                river.save()
            else:
                river = River.objects.filter(name_jp=riv_name_jp)[0]

            river.prefecture.add(prefecture)
            river.region.add(region)

            col = row.find_all("td")[0]
            dam_url = ("http://www.river.go.jp/kawabou/ipDamKobetu.do?init=init&obsrvId=" +
                       col.a.get('href').split("'")[3] +
                       "&gamenId=01-1004&timeType=60&requestType=1&fldCtlParty=no")
            if not Dam.objects.filter(url=dam_url):
                dam_name_jp = col.a.text.strip()
                dam_name = translator.translate(dam_name_jp, src='ja', dest='ja').pronunciation
                if not dam_name:
                    dam_name = translator.translate(dam_name_jp, src='ja', dest='en').text
                if " damu" in dam_name:
                    dam_name = dam_name.replace("damu", "Dam")
                elif "damu" in dam_name:
                    dam_name = dam_name.replace("damu", " Dam")
                dam = Dam(name_jp=dam_name_jp, name=dam_name, url=dam_url)
                dam.save()
            else:
                dam = Dam.objects.filter(url=dam_url)[0]

            dam.river.add(river)

