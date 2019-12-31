from django.urls import path
from . import views
from .views import RiverCreateView, RiverDetailView

urlpatterns = [
    path('', views.rivermap, name="rivermap"),
    path('river/<int:pk>/', RiverDetailView.as_view(), name='river-detail'),
    path('river/new/', RiverCreateView.as_view(), name='river-create'),
]
