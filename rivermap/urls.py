from django.urls import path
from . import views
from .views import RiverCreateView, RiverDetailView, RiverUpdateView, RiverListView, PrefectureListView, \
    PrefectureDetailView

urlpatterns = [
    path('', views.rivermap, name="rivermap"),
    path('river/<slug:slug>/', RiverListView.as_view(), name='river-list'),
    path('river/', PrefectureListView.as_view(), name='prefecture-list'),
    path('river/<slug:slug>/<int:pk>/', RiverDetailView.as_view(), name='river-detail'),
    # path('river/<slug:slug>/', PrefectureDetailView.as_view(), name='prefecture-detail'),
    path('river/new/', RiverCreateView.as_view(), name='river-create'),
    path('river/<int:pk>/update/', RiverUpdateView.as_view(), name='river-update'),
]
