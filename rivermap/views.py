import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.safestring import mark_safe
from django.views.generic import DetailView, UpdateView, ListView, DeleteView
from googletrans import Translator
from django.utils.translation import gettext as _

from .models import River, Prefecture, Section, Region, Spot, Comment
from .forms import SectionAddForm, SectionEditForm, CommentAddForm, ObjectAddForm, SpotAddForm, \
    SpotEditForm
from .utils import json_comments, json_sections, json_spots, calculate_distance


def rivermap(request):
    if request.method == "POST":
        object_type = request.POST.get('object_type')
        if object_type == 'spot':
            section = get_object_or_404(Spot, pk=request.POST.get('section'))
        elif object_type == 'section':
            section = get_object_or_404(Section, pk=request.POST.get('section'))
        form = CommentAddForm(request.POST, request.FILES)
        comment = form.save(commit=False)
        comment.author = request.user
        comment.parent = section
        comment.save()

        response_data = json_comments()
        json_sections()
        json_spots()

        return JsonResponse(response_data)
    else:
        form = CommentAddForm
        return render(request, 'rivermap/map.html', {'title': 'Map', 'form': form})


class RiverListView(ListView):
    model = River
    context_object_name = 'rivers'
    ordering = ['name']
    paginate_by = 50

    def get_queryset(self):
        return River.objects.filter(prefecture__slug=self.kwargs['prefecture']).annotate(count=Count('section')+Count('spot')).order_by('-count', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prefecture'] = get_object_or_404(Prefecture, slug=self.kwargs['prefecture'])
        return context


class SectionListView(ListView):
    model = Section
    template_name = 'rivermap/riverobject_list.html'
    context_object_name = 'sections'
    ordering = ['name']
    paginate_by = 50

    def get_queryset(self):
        return Section.objects.filter(prefecture__slug=self.kwargs['prefecture']).order_by(Lower('name'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prefecture'] = get_object_or_404(Prefecture, slug=self.kwargs['prefecture'])
        context['object_type'] = 0
        context['detail_url'] = 'section-detail'
        return context


class SpotListView(ListView):
    model = Spot
    template_name = 'rivermap/riverobject_list.html'
    context_object_name = 'sections'
    ordering = ['name']
    paginate_by = 50

    def get_queryset(self):
        return Spot.objects.filter(prefecture__slug=self.kwargs['prefecture']).order_by(Lower('name'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prefecture'] = get_object_or_404(Prefecture, slug=self.kwargs['prefecture'])
        context['object_type'] = 1
        context['detail_url'] = 'spot-detail'
        return context


class PrefectureListView(ListView):
    model = Prefecture
    context_object_name = 'prefectures'
    ordering = ['pk']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.all  # get_object_or_404(Prefecture, slug=self.kwargs['prefecture'])
        return context


class RiverDetailView(DetailView):
    model = River

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prefecture'] = get_object_or_404(Prefecture, slug=self.kwargs['prefecture'])
        return context


class SectionDetailView(DetailView):
    template_name = 'rivermap/riverobject_detail.html'
    model = Section
    form_class = CommentAddForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['edit_url'] = 'section-update'
        context['object_type'] = 0
        context['form'] = self.form_class(initial={'parent': self.object})
        context['comments'] = self.object.mapobjectcomment_set.all().order_by('-date_posted')
        context['distance'] = calculate_distance(self.object.lat, self.object.lng, self.object.end_lat, self.object.end_lng)
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        form.instance.author = request.user
        if form.is_valid():
            form.save()
        response_data = json_comments()
        response_data['imageSize'] = 'main'
        print(response_data)
        json_sections()
        return JsonResponse(response_data)


class SpotDetailView(DetailView):
    template_name = 'rivermap/riverobject_detail.html'
    model = Spot
    form_class = CommentAddForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['edit_url'] = 'spot-update'
        context['object_type'] = 1
        context['form'] = self.form_class(initial={'parent': self.object})
        context['comments'] = self.object.mapobjectcomment_set.all().order_by('-date_posted')
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        form.instance.author = request.user
        if form.is_valid():
            form.save()
        response_data = json_comments()
        response_data['imageSize'] = 'main'
        json_spots()
        return JsonResponse(response_data)


class PrefectureDetailView(DetailView):
    model = Prefecture


@login_required
def add_object(request):
    translator = Translator()
    if request.method == 'POST':
        if 'add_object' in request.POST:
            print(request.POST)
            if request.POST.get('object_type') == '1':
                prefecture = get_object_or_404(Prefecture, slug=request.POST.get('prefecture'))
                if 'river' in request.POST:
                    river = get_object_or_404(River, pk=request.POST.get('river'))
                    form = SectionAddForm(initial={'river': river, 'prefecture': prefecture})
                else:
                    form = SectionAddForm(initial={'prefecture': prefecture})
                form.fields['river'].queryset = River.objects.filter(prefecture=prefecture).order_by('name')
                return render(request, 'rivermap/add_section.html', {'form': form, 'prefecture': prefecture})

            elif request.POST.get('object_type') == '2':
                prefecture = get_object_or_404(Prefecture, slug=request.POST.get('prefecture'))
                if 'river' in request.POST:
                    river = get_object_or_404(River, pk=request.POST.get('river'))
                    form = SpotAddForm(initial={'river': river, 'prefecture': prefecture})
                else:
                    form = SpotAddForm(initial={'prefecture': prefecture})
                form.fields['river'].queryset = River.objects.filter(prefecture=prefecture).order_by('name')
                return render(request, 'rivermap/add_spot.html', {'form': form, 'prefecture': prefecture})

        else:
            if 'add_section' in request.POST:
                form = SectionAddForm(request.POST)
            elif 'add_spot' in request.POST:
                form = SpotAddForm(request.POST)
            else:
                form = ObjectAddForm
                return render(request, 'rivermap/add_object.html', {'form': form})
            if form.is_valid():
                river_object = form.save(commit=False)
                river_object.region = river_object.prefecture.region
                river_object.name = river_object.name_jp
                river_object.author = request.user
                if re.search(u'[\u3000-\u9fff]', river_object.name):
                    try:
                        river_object.name = translator.translate(river_object.name_jp, src='ja', dest='en').text
                    except ValueError:
                        pass
                else:
                    try:
                        river_object.name_jp = translator.translate(river_object.name, src='en', dest='ja').text
                    except ValueError:
                        pass
                river_object.save()
                message = _('The new section has successfully been saved!') + '</br>' + \
                          _('Please add some more details about the river') + '</br>' + \
                          _('The river will appear on the map soon')
                message = mark_safe(message)
                messages.success(request, message)
                if 'add_section' in request.POST:
                    return redirect('section-update', pk=river_object.id)
                elif 'add_spot' in request.POST:
                    return redirect('spot-update', pk=river_object.id)
                form = ObjectAddForm
                return render(request, 'rivermap/add_object.html', {'form': form})
            else:
                river = get_object_or_404(River, pk=request.POST.get('river'))
                prefecture = get_object_or_404(Prefecture, slug=request.POST.get('prefecture'))
                return render(request, 'rivermap/add_section.html',
                              {'form': form, 'river': river, 'prefecture': prefecture})
    else:
        form = ObjectAddForm
    return render(request, 'rivermap/add_object.html', {'form': form})


class SectionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'rivermap/riverobject_form.html'
    model = Section
    form_class = SectionEditForm

    def get_form(self, form_class=None):
        form = super(SectionUpdateView, self).get_form(form_class)
        form.fields["observatory"].queryset = self.object.river.system_observatories_set()
        form.fields["dam"].queryset = self.object.river.system_dams_set()
        if self.object.difficulty:
            diff_split = self.object.difficulty.split(' ')
            form.fields["average_difficulty"].initial = diff_split[0]
            if len(diff_split) > 1:
                form.fields["max_difficulty"].initial = diff_split[1].replace('(', '').replace(')', '')
        return form

    def form_valid(self, form):
        if not form.instance.author:
            form.instance.author = self.request.user
        cleaned_average = form.cleaned_data['average_difficulty']
        cleaned_max = form.cleaned_data['max_difficulty']
        if cleaned_average == 'None':
            form.instance.difficulty = ''
        elif cleaned_max == 'None' or cleaned_average == cleaned_max:
            form.instance.difficulty = cleaned_average
        else:
            form.instance.difficulty = cleaned_average + ' (' + cleaned_max + ')'
        redirect_url = super().form_valid(form)
        json_sections()
        return redirect_url

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.groups.filter(name='Super Paddler'):
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = 2
        return context


class SpotUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'rivermap/riverobject_form.html'
    model = Spot
    form_class = SpotEditForm

    def get_form(self, form_class=None):
        form = super(SpotUpdateView, self).get_form(form_class)
        form.fields["observatory"].queryset = self.object.river.system_observatories_set()
        form.fields["dam"].queryset = self.object.river.system_dams_set()
        if self.object.difficulty:
            form.fields["average_difficulty"].initial = self.object.difficulty
        return form

    def form_valid(self, form):
        if not form.instance.author:
            form.instance.author = self.request.user
        cleaned_average = form.cleaned_data['average_difficulty']
        if cleaned_average == 'None':
            form.instance.difficulty = ''
        else:
            form.instance.difficulty = cleaned_average
        redirect_url = super().form_valid(form)
        json_spots()
        return redirect_url

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.groups.filter(name='Super Paddler'):
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = 3
        return context


def how_to_add(request):
    return render(request, 'rivermap/how_to_add.html', {'title': 'Help'})


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'rivermap/comment_form.html'
    model = Comment
    form_class = CommentAddForm

    def form_valid(self, form):
        if not form.instance.author:
            form.instance.author = self.request.user
        redirect_url = super().form_valid(form)
        json_comments()
        return redirect_url

    def test_func(self):
        comment = self.get_object()
        if self.request.user == comment.author or self.request.user.is_staff:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(CommentUpdateView, self).get_context_data(**kwargs)
        context['isUpdate'] = True
        context['numPics'] = self.object.num_pics()
        context['cancel_link'] = self.object.parent.get_absolute_url()
        return context


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = 'rivermap/comment_confirm_delete.html'
    model = Comment
    form_class = CommentAddForm

    def test_func(self):
        comment = self.get_object()
        if self.request.user == comment.author or self.request.user.is_staff:
            return True
        return False

    def get_success_url(self):
        return self.object.parent.get_absolute_url()
