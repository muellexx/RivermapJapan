from django.urls import path
from . import views
from .views import RiverCreateView, RiverDetailView, RiverUpdateView, RiverListView, PrefectureListView, \
    PrefectureDetailView

urlpatterns = [
    path('', views.rivermap, name="rivermap"),
    path('map/<slug:prefecture>/river/', RiverListView.as_view(), name='river-list'),
    path('map/river/', PrefectureListView.as_view(), name='prefecture-list'),
    path('map/<slug:prefecture>/river/<int:pk>/', RiverDetailView.as_view(), name='river-detail'),
    path('map/<slug:slug>/', PrefectureDetailView.as_view(), name='prefecture-detail'),
    path('map/river/new/', RiverCreateView.as_view(), name='river-create'),
    path('map/river/<int:pk>/update/', RiverUpdateView.as_view(), name='river-update'),
    path('map/section/add/', views.add_section, name='add-section'),
]
