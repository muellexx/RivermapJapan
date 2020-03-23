from django.urls import path
from . import views
from .views import RiverDetailView, RiverListView, \
    PrefectureListView, PrefectureDetailView, \
    SectionDetailView, SectionUpdateView, SectionListView, SpotUpdateView, SpotDetailView, SpotListView

urlpatterns = [
    path('', views.rivermap, name="rivermap"),
    path('map/<slug:prefecture>/river/', RiverListView.as_view(), name='river-list'),
    path('map/<slug:prefecture>/section/', SectionListView.as_view(), name='section-list'),
    path('map/<slug:prefecture>/spot/', SpotListView.as_view(), name='spot-list'),
    path('map/river/', PrefectureListView.as_view(), name='prefecture-list'),
    path('map/<slug:prefecture>/river/<int:pk>/', RiverDetailView.as_view(), name='river-detail'),
    path('map/river/<int:pk>/', RiverDetailView.as_view(), name='river-detail'),
    path('map/<slug:prefecture>/section/<int:pk>/', SectionDetailView.as_view(), name='section-detail'),
    path('map/<slug:prefecture>/spot/<int:pk>/', SpotDetailView.as_view(), name='spot-detail'),
    path('map/<slug:slug>/', PrefectureDetailView.as_view(), name='prefecture-detail'),
    path('map/object/add/', views.add_object, name='add-object'),
    path('map/section/<int:pk>/update/', SectionUpdateView.as_view(), name='section-update'),
    path('map/spot/<int:pk>/update/', SpotUpdateView.as_view(), name='spot-update'),
    path('map/object/how-to-add/', views.how_to_add, name="how-to-add"),
]
