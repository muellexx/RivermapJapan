from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import CreateView, DetailView

from .models import River


def rivermap(request):
    rivers = River.objects.all()
    return render(request, 'rivermap/map.html', {'title': 'Map', 'rivers': rivers})


class RiverDetailView(DetailView):
    model = River


class RiverCreateView(LoginRequiredMixin, CreateView):
    model = River
    fields = ['name', 'url', 'level', 'date', 'high_water', 'middle_water', 'low_water', 'start_lat', 'start_lng',
              'end_lat', 'end_lng', 'difficulty', 'section']
    success_url = '/'

    def form_valid(self, form):
        return super().form_valid(form)

