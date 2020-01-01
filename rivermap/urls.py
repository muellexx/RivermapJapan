from django.urls import path
from . import views
from .views import RiverCreateView, RiverDetailView, RiverUpdateView, RiverListView

urlpatterns = [
    path('', views.rivermap, name="rivermap"),
    path('river/', RiverListView.as_view(), name='river-list'),
    path('river/<int:pk>/', RiverDetailView.as_view(), name='river-detail'),
    path('river/new/', RiverCreateView.as_view(), name='river-create'),
    path('river/<int:pk>/update/', RiverUpdateView.as_view(), name='river-update'),
]
