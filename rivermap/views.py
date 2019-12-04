from django.shortcuts import render
from .models import River


def index(request):
    rivers = River.objects.all()
    return render(request, 'rivermap/index.html', {'rivers': rivers})
