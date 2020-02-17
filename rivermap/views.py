import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, DetailView, UpdateView, ListView
from googletrans import Translator
from django.utils.translation import gettext as _

from .models import River, Prefecture, Section
from .forms import SectionAddForm, SectionEditForm, CommentAddForm
from .utils import json_comments, json_sections, scrape_sections


def rivermap(request):
    response_data = {}
    if request.method == "POST":
        section = get_object_or_404(Section, pk=request.POST.get('section'))
        form = CommentAddForm(request.POST)
        comment = form.save(commit=False)
        comment.author = request.user
        comment.parent = section
        comment.save()

        response_data['image_url'] = comment.author.profile.image.url
        response_data['author'] = comment.author.username
        response_data['date_posted'] = timezone.localtime(comment.date_posted).strftime('%B %d, %Y')
        response_data['title'] = request.POST.get('title')
        response_data['content'] = request.POST.get('content')
        json_comments()
        json_sections()

        return JsonResponse(response_data)
    else:
        form = CommentAddForm
        return render(request, 'rivermap/map.html', {'title': 'Map', 'form': form})


class RiverListView(ListView):
    model = River
    # template_name = 'rivermap/river_list.html'
    context_object_name = 'rivers'
    ordering = ['name']
    paginate_by = 50

    def get_queryset(self):
        return River.objects.filter(prefecture__slug=self.kwargs['prefecture']).order_by(Lower('name'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.kwargs['prefecture'])
        print(Prefecture.objects.get(slug=self.kwargs['prefecture']))
        context['prefecture'] = get_object_or_404(Prefecture, slug=self.kwargs['prefecture'])
        return context


class SectionListView(ListView):
    model = Section
    context_object_name = 'sections'
    ordering = ['name']
    paginate_by = 50

    def get_queryset(self):
        return Section.objects.filter(prefecture__slug=self.kwargs['prefecture']).order_by(Lower('name'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.kwargs['prefecture'])
        print(Prefecture.objects.get(slug=self.kwargs['prefecture']))
        context['prefecture'] = get_object_or_404(Prefecture, slug=self.kwargs['prefecture'])
        return context


class PrefectureListView(ListView):
    model = Prefecture
    context_object_name = 'prefectures'
    ordering = ['pk']


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
    translator = Translator()
    if request.method == 'POST':
        if 'prepair_comment' in request.POST:
            river = get_object_or_404(River, pk=request.POST.get('river'))
            prefecture = get_object_or_404(Prefecture, slug=request.POST.get('prefecture'))
            print(prefecture.name)
            form = SectionAddForm
            return render(request, 'rivermap/add_section.html',
                          {'form': form, 'river': river, 'prefecture': prefecture})
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
                if re.search(u'[\u3000-\u9fff]', section.name):
                    try:
                        section.name = translator.translate(section.name_jp, src='ja', dest='en').text
                    except ValueError:
                        pass
                else:
                    try:
                        section.name_jp = translator.translate(section.name, src='en', dest='ja').text
                    except ValueError:
                        pass
                section.save()
                # message = f'The new section has successfully been saved!</br>' \
                #           f'Please add some more details about the river</br>' \
                #           f'The river will appear on the map after it has been reviewed by an admin'
                message = _('The new section has successfully been saved!') + '</br>' + \
                          _('Please add some more details about the river') + '</br>' + \
                          _('The river will appear on the map soon')
                message = mark_safe(message)
                messages.success(request, message)
                return redirect('section-update', pk=section.id)
            else:
                river = get_object_or_404(River, pk=request.POST.get('river'))
                prefecture = get_object_or_404(Prefecture, slug=request.POST.get('prefecture'))
                return render(request, 'rivermap/add_section.html',
                              {'form': form, 'river': river, 'prefecture': prefecture})
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
        redirect_url = super().form_valid(form)
        scrape_sections()
        json_sections()
        return redirect_url

    def test_func(self):
        print(self.get_object())
        print(self.request.user)
        print(self.get_object().author)
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
