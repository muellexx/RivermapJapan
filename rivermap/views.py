from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import CreateView, DetailView, UpdateView, ListView

from .models import River, Prefecture


def rivermap(request):
    rivers = River.objects.all()
    return render(request, 'rivermap/map.html', {'title': 'Map', 'rivers': rivers})


# class RiverListView(ListView):
#     model = River
#     template_name = 'rivermap/home.html'
#     context_object_name = 'rivers'
#     ordering = ['name']
#     paginate_by = 5


class RiverListView(ListView):
    model = River
    template_name = 'rivermap/home.html'
    context_object_name = 'rivers'
    ordering = ['name']
    paginate_by = 20

    def get_queryset(self):
        #return River.objects.filter(prefecture__slug="hokkaido")
        return River.objects.filter(prefecture__slug=self.kwargs['slug'])


class PrefectureListView(ListView):
    model = Prefecture
    # template_name = 'rivermap/prefecture_list.html'
    context_object_name = 'prefectures'
    ordering = ['pk']
    # paginate_by = 5


class RiverDetailView(DetailView):
    model = River


class PrefectureDetailView(DetailView):
    model = Prefecture


class RiverCreateView(LoginRequiredMixin, CreateView):
    model = River
    fields = ['name', 'url', 'high_water', 'middle_water', 'low_water', 'start_lat', 'start_lng',
              'end_lat', 'end_lng', 'difficulty', 'section']


class RiverUpdateView(LoginRequiredMixin, UpdateView):
    model = River
    fields = ['name', 'url', 'high_water', 'middle_water', 'low_water', 'start_lat', 'start_lng',
              'end_lat', 'end_lng', 'difficulty', 'section']
