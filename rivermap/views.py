from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import CreateView, DetailView, UpdateView, ListView

from .models import River


def rivermap(request):
    rivers = River.objects.all()
    return render(request, 'rivermap/map.html', {'title': 'Map', 'rivers': rivers})


class RiverListView(ListView):
    model = River
    template_name = 'rivermap/home.html'
    context_object_name = 'rivers'
    ordering = ['name']
    paginate_by = 5


class RiverDetailView(DetailView):
    model = River


class RiverCreateView(LoginRequiredMixin, CreateView):
    model = River
    fields = ['name', 'url', 'high_water', 'middle_water', 'low_water', 'start_lat', 'start_lng',
              'end_lat', 'end_lng', 'difficulty', 'section']


class RiverUpdateView(LoginRequiredMixin, UpdateView):
    model = River
    fields = ['name', 'url', 'high_water', 'middle_water', 'low_water', 'start_lat', 'start_lng',
              'end_lat', 'end_lng', 'difficulty', 'section']
