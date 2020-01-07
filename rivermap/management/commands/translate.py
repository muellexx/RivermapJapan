from django.core.management.base import BaseCommand

from googletrans import Translator
from rivermap.models import River, Observatory, Dam


class Command(BaseCommand):
    help = 'Translate names of Rivers, Observatories and Dams to English'

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
                    print(river.name)
                    river.save()
                except ValueError:
                    limit_reached = True

        rivers = Observatory.objects.all()
        for river in rivers:
            if limit_reached:
                break
            if river.name == 'TODO':
                try:
                    river.name = translator.translate(river.name_jp, src='ja', dest='ja').pronunciation
                    if not river.name:
                        river.name = translator.translate(river.name_jp, src='ja', dest='en').text
                    print(river.name)
                    river.save()
                except ValueError:
                    limit_reached = True

        rivers = Dam.objects.all()
        for river in rivers:
            if limit_reached:
                break
            if river.name == 'TODO':
                try:
                    river.name = translator.translate(river.name_jp, src='ja', dest='ja').pronunciation
                    if not river.name:
                        river.name = translator.translate(river.name_jp, src='ja', dest='en').text
                    if river.name.endswith(" damu"):
                        river.name = river.name.replace("damu", "Dam")
                    elif river.name.endswith("damu"):
                        river.name = river.name.replace("damu", " Dam")
                    else:
                        river.name = river.name + " Dam"
                    print(river.name)
                    river.save()
                except ValueError:
                    limit_reached = True

        if limit_reached:
            print("Limit Reached!")
        else:
            print("Finished")
