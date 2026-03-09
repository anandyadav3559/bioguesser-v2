from django.urls import path
from .views import PaginatedAnimalView

urlpatterns = [
    path('animals/', PaginatedAnimalView.as_view(), name='paginated_animals'),
]
