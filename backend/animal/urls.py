from django.urls import path
from .views import AnimalDetailView, AnimalBatchView
from .serializer import AnimalBasicSerializer

urlpatterns = [
    path("animal/<uuid:animal_id>", AnimalDetailView.as_view()),
    path("batch/", AnimalBatchView.as_view()),
]