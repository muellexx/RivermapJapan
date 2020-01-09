from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, DetailView, UpdateView, ListView

from .models import River, Prefecture
from .forms import SectionAddForm


def rivermap(request):
    rivers = River.objects.all()
    return render(request, 'rivermap/map.html', {'title': 'Map', 'rivers': rivers})


class RiverListView(ListView):
    model = River
    # template_name = 'rivermap/river_list.html'
    context_object_name = 'rivers'
    ordering = ['name']
    paginate_by = 20

    def get_queryset(self):
        return River.objects.filter(prefecture__slug=self.kwargs['prefecture']).order_by('name')


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


@login_required
def add_section(request):
    if request.method == 'POST':
        if 'prepair_comment' in request.POST:
            river = get_object_or_404(River, pk=request.POST.get('river'))
            prefecture = get_object_or_404(Prefecture, slug=request.POST.get('prefecture'))
            print(prefecture.name)
            form = SectionAddForm
            return render(request, 'rivermap/add_section.html', {'form': form, 'river': river, 'prefecture': prefecture})
        else:
            form = SectionAddForm(request.POST)
            if form.is_valid():
                river = get_object_or_404(River, pk=request.POST.get('river'))
                prefecture = get_object_or_404(Prefecture, slug=request.POST.get('prefecture'))
                section = form.save(commit=False)
                section.river = river
                section.prefecture = prefecture
                section.region = prefecture.region
                print(section.river)
                print(section.prefecture)
                print(section.region)
                return HttpResponse('thanks')
    else:
        form = SectionAddForm
    return render(request, 'rivermap/add_section.html', {'form': form})
