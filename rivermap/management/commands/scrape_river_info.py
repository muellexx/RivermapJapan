import sys

from bs4 import BeautifulSoup as soup
from django.core.management.base import BaseCommand
from urllib.request import urlopen as uReq
from selenium import webdriver

from googletrans import Translator
from rivermap.models import Prefecture, River, Observatory, Dam


class Command(BaseCommand):
    help = 'Scape Info of all the rivers in Japan'

    def handle(self, *args, **options):
        translator = Translator()

        main_url = "http://www.river.go.jp/kawabou/ipAreaJump.do?gamenId=01-0201&refineType=1&fldCtlParty=no"
        uClient = uReq(main_url)
        main_page_html = uClient.read()
        uClient.close()
        main_page_soup = soup(main_page_html, "lxml")
        table = main_page_soup.find("table", {"class": "jumptable"})
        pref_urls = main_page_soup.find("table", {"class": "jumptable"}).find_all('a')
        start = False
        io_error_counter = 0
        io_error_counter_max = 600

        for pref_url in pref_urls:
            limit_reached = False
            if not pref_url.get('onclick').split("(")[1].split(")")[0].replace("'", "").split(",")[1]:
                continue
            url = "http://www.river.go.jp/kawabou/ipGaikyoMap.do?areaCd=" + \
                  pref_url.get('onclick').split("(")[1].split(")")[0].replace("'", "").split(",")[0] + "&prefCd=" + \
                  pref_url.get('onclick').split("(")[1].split(")")[0].replace("'", "").split(",")[1] + \
                  "&townCd=&gamenId=01-0704&fldCtlParty=no"
            pref_name = pref_url.text.strip()
            if "北海道" in pref_name:
                pref_name = "北海道"
            prefecture = Prefecture.objects.filter(name_jp=pref_name)[0]
            region = prefecture.region
            if prefecture.name == "Kumamoto":
                start = True
            if not start:
                continue
            print(pref_name)
            driver = webdriver.Firefox()
            uClient = uReq(url)
            page_html = uClient.read()
            uClient.close()
            page_soup = soup(page_html, "html.parser")
            observatory_url = "http://www.river.go.jp" + page_soup.find("div", {"class": "obsdata-box"}).find_all('a')[1].\
                get('href')
            try:
                dam_url = "http://www.river.go.jp" + page_soup.find("div", {"class": "obsdata-box"}).find_all('a')[2].\
                    get('href')
            except IndexError:
                dam_url = ''

            driver.get(observatory_url)
            has_next_page = True

            while has_next_page:
                if io_error_counter > io_error_counter_max:
                    print("exit for safety reasons regarding disk i/o error, run again to continue")
                    driver.close()
                    sys.exit()
                sub_page_soup = soup(driver.page_source, 'html.parser')
                rows = sub_page_soup.find("div", {"class": "gaikyoCntt"}).table.find_all("tr")[2:]

                for row in rows:

                    col = row.find_all("td")[2]
                    riv_name_jp = col.text.strip()
                    if riv_name_jp == 'その他':
                        continue

                    if not River.objects.filter(name_jp=riv_name_jp):
                        print("  riv " + riv_name_jp)
                        if limit_reached:
                            riv_name = "TODO"
                        else:
                            try:
                                riv_name = translator.translate(riv_name_jp, src='ja', dest='ja').pronunciation
                                if not riv_name:
                                    riv_name = translator.translate(riv_name_jp, src='ja', dest='en').text
                                if riv_name.endswith("gawa"):
                                    riv_name = riv_name.replace("gawa", " River")
                                elif riv_name.endswith("kawa"):
                                    riv_name = riv_name.replace("kawa", " River")
                                elif "River" not in riv_name:
                                    riv_name = riv_name + " River"
                                elif " River" not in riv_name:
                                    riv_name.replace("River", " River")
                            except ValueError:
                                riv_name = "TODO"
                                limit_reached = True
                                print("  --googletrans limit reached--")
                        river = River(name_jp=riv_name_jp, name=riv_name)
                        river.save()
                        io_error_counter = io_error_counter + 1
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
                        print("  obs " + obs_name_jp)
                        if limit_reached:
                            obs_name = "TODO"
                        else:
                            try:
                                obs_name = translator.translate(obs_name_jp, src='ja', dest='ja').pronunciation
                                if not obs_name:
                                    obs_name = translator.translate(obs_name_jp, src='ja', dest='en').text
                            except ValueError:
                                obs_name = "TODO"
                                limit_reached = True
                                print("  --googletrans limit reached--")
                        observatory = Observatory(name_jp=obs_name_jp, name=obs_name, url=obs_url, region=region,
                                                  prefecture=prefecture)
                        observatory.save()
                        io_error_counter = io_error_counter + 1
                    else:
                        observatory = Observatory.objects.filter(url=obs_url)[0]

                    observatory.river.add(river)

                try:
                    driver.find_elements_by_xpath('//td[@class="comHeaderLbl"]')[2].find_elements_by_xpath('a')[0].\
                        click()
                except IndexError:
                    has_next_page = False

            if dam_url == '':
                continue

            driver.get(dam_url)
            has_next_page = True

            while has_next_page:
                if io_error_counter > io_error_counter_max:
                    print("exit for safety reasons regarding disk i/o error, run again to continue")
                    driver.close()
                    sys.exit()
                sub_page_soup = soup(driver.page_source, 'html.parser')
                rows = sub_page_soup.find("div", {"class": "gaikyoCntt"}).table.find_all("tr")[1:]

                for row in rows:

                    col = row.find_all("td")[2]
                    riv_name_jp = col.text.strip()
                    if riv_name_jp == 'その他':
                        continue

                    if not River.objects.filter(name_jp=riv_name_jp):
                        print("  riv " + riv_name_jp)
                        if limit_reached:
                            riv_name = "TODO"
                        else:
                            try:
                                riv_name = translator.translate(riv_name_jp, src='ja', dest='ja').pronunciation
                                if not riv_name:
                                    riv_name = translator.translate(riv_name_jp, src='ja', dest='en').text
                                if riv_name.endswith("gawa"):
                                    riv_name = riv_name.replace("gawa", " River")
                                elif riv_name.endswith("kawa"):
                                    riv_name = riv_name.replace("kawa", " River")
                                elif "River" not in riv_name:
                                    riv_name = riv_name + " River"
                                elif " River" not in riv_name:
                                    riv_name.replace("River", " River")
                            except ValueError:
                                riv_name = "TODO"
                                limit_reached = True
                                print("  --googletrans limit reached--")
                        river = River(name_jp=riv_name_jp, name=riv_name)
                        river.save()
                        io_error_counter = io_error_counter + 1
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
                        print("    " + dam_name_jp)
                        if limit_reached:
                            dam_name = "TODO"
                        else:
                            try:
                                dam_name = translator.translate(dam_name_jp, src='ja', dest='ja').pronunciation
                                if not dam_name:
                                    dam_name = translator.translate(dam_name_jp, src='ja', dest='en').text
                                if dam_name.endswith(" damu"):
                                    dam_name = dam_name.replace("damu", "Dam")
                                elif dam_name.endswith("damu"):
                                    dam_name = dam_name.replace("damu", " Dam")
                                else:
                                    dam_name = dam_name + " Dam"
                            except ValueError:
                                dam_name = "TODO"
                                limit_reached = True
                                print("  --googletrans limit reached--")
                        dam = Dam(name_jp=dam_name_jp, name=dam_name, url=dam_url, region=region, prefecture=prefecture)
                        dam.save()
                        io_error_counter = io_error_counter + 1
                    else:
                        dam = Dam.objects.filter(url=dam_url)[0]

                    dam.river.add(river)

                try:
                    driver.find_elements_by_xpath('//td[@class="comHeaderLbl"]')[2].find_elements_by_xpath('a')[0].\
                        click()
                except IndexError:
                    has_next_page = False

            driver.close()
