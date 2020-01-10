from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, DetailView, UpdateView, ListView

from .models import River, Prefecture, Section
from .forms import SectionAddForm, SectionEditForm


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


class SectionListView(ListView):
    model = Section
    # template_name = 'rivermap/river_list.html'
    context_object_name = 'sections'
    ordering = ['name']
    paginate_by = 20

    def get_queryset(self):
        return Section.objects.filter(prefecture__slug=self.kwargs['prefecture']).order_by('name')


class PrefectureListView(ListView):
    model = Prefecture
    # template_name = 'rivermap/prefecture_list.html'
    context_object_name = 'prefectures'
    ordering = ['pk']
    # paginate_by = 5


class RiverDetailView(DetailView):
    model = River


class SectionDetailView(DetailView):
    model = Section


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
                section.name = section.name_jp
                section.author = request.user
                section.save()
                message = f'The new section has successfully been saved!</br>' \
                          f'Please add some more details about the river</br>' \
                          f'The river will appear on the map after it has been reviewed by an admin'
                message = mark_safe(message)
                messages.success(request, message)
                return redirect('section-update', pk=section.id)
    else:
        form = SectionAddForm
    return render(request, 'rivermap/add_section.html', {'form': form})


class SectionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Section
    form_class = SectionEditForm

    def get_form(self, form_class=None):
        form = super(SectionUpdateView, self).get_form(form_class)
        form.fields["observatory"].queryset = self.object.river.observatory_set.all()
        form.fields["dam"].queryset = self.object.river.dam_set.all()
        return form

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        print(self.get_object())
        print(self.request.user)
        print(self.get_object().author)
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
