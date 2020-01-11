from django.urls import path
from . import views
from .views import RiverDetailView, RiverUpdateView, RiverListView, \
    PrefectureListView, PrefectureDetailView, \
    SectionDetailView, SectionUpdateView, SectionListView, RiverCreateView

urlpatterns = [
    path('', views.rivermap, name="rivermap"),
    path('map/<slug:prefecture>/river/', RiverListView.as_view(), name='river-list'),
    path('map/<slug:prefecture>/section/', SectionListView.as_view(), name='section-list'),
    path('map/river/', PrefectureListView.as_view(), name='prefecture-list'),
    path('map/<slug:prefecture>/river/<int:pk>/', RiverDetailView.as_view(), name='river-detail'),
    path('map/river/<int:pk>/', RiverDetailView.as_view(), name='river-detail'),
    path('map/<slug:prefecture>/section/<int:pk>/', SectionDetailView.as_view(), name='section-detail'),
    path('map/<slug:slug>/', PrefectureDetailView.as_view(), name='prefecture-detail'),
    path('map/river/new/', RiverCreateView.as_view(), name='river-create'),
    path('map/river/<int:pk>/update/', RiverUpdateView.as_view(), name='river-update'),
    path('map/section/add/', views.add_section, name='add-section'),
    path('map/section/<int:pk>/update/', SectionUpdateView.as_view(), name='section-update'),
]
