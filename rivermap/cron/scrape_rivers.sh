#!/usr/bin/env bash
cd /home/alex/RivermapJapan
source venv/bin/activate
python manage.py scrape_rivers
chmod 777 testfile.csv