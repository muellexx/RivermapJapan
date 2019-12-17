import json
import sqlite3
from bs4 import BeautifulSoup as soup
from django.core.management.base import BaseCommand, CommandError
from urllib.request import urlopen as uReq


class Command(BaseCommand):
    help = 'Scrape water level of the rivers'

    def handle(self, *args, **options):
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute("SELECT * FROM rivermap_river")
        rows = cur.fetchall()
        for row in rows:
            river_id = '0' * (3 - len(str(row[0]))) + str(row[0])
            river_name = row[1]
            url = row[2]

            # opening up connection, grabbing page, closing connection
            uClient = uReq(url)
            page_html = uClient.read()
            uClient.close()

            # html parsing
            page_soup = soup(page_html, "html.parser")

            # get the table and the rows
            table = page_soup.find("div", {"id": "hyou"}).table
            bs4rows = table.find_all("tr")

            # Create and initialize file for result
            filename = 'test' + river_id + '(' + river_name.replace(" ", "_") + ').json'

            data = {'level': []}

            date = '0'
            # loop through the rows of the table
            for bs4row in bs4rows:
                cells = bs4row.find_all("td")
                time = cells[0].text.strip()
                if len(time.split(' ')) > 1:
                    date = time.split(' ')[0]
                    time = time.split(' ')[1]
                level = cells[1].text.strip()
                try:
                    level = float(level)
                    current_level = level
                    current_date_time = date + ' ' + time
                except ValueError:
                    pass

                data['level'].append({
                    'date': date,
                    'time': time,
                    'level': level,
                })

            with open(filename, 'w') as outfile:
                json.dump(data, outfile, indent=4)

            sql = '''UPDATE rivermap_river
                     SET date = ?,
                         level = ?
                     WHERE id = ?'''
            new_cur = conn.cursor()
            try:
                new_cur.execute(sql, (current_date_time, current_level, row[0]))
                conn.commit()
                del current_date_time, current_level
            except NameError:
                pass

        ncur = conn.cursor()
        ncur.execute("SELECT * FROM rivermap_river")
        rows = ncur.fetchall()
        rivers = {'rivers': []}
        for row in rows:
            rivers['rivers'].append({
                'id': row[0],
                'name': row[1],
                'url': row[2],
                'level': row[3],
                'date': row[8],
                'high_water': row[9],
                'middle_water': row[11],
                'low_water': row[10],
                'start_lat': row[4],
                'start_lng': row[5],
                'end_lat': row[6],
                'end_lng': row[7],
            })

        with open('testriver.json', 'w') as outfile:
            json.dump(rivers, outfile, indent=4)

        conn.close()
