from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from animal.models import Animal
from animal.serializer import AnimalBasicSerializer

class AnimalPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class PaginatedAnimalView(generics.ListAPIView):
    queryset = Animal.objects.all().order_by('name')
    serializer_class = AnimalBasicSerializer
    pagination_class = AnimalPagination
