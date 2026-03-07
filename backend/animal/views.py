
# Create your views here.
import random
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Animal, AnimalLocation, AnimalCharacteristic
from .serializer import AnimalDetailSerializer, AnimalBasicSerializer

class AnimalDetailView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, animal_id):
        animal = get_object_or_404(
            Animal.objects.prefetch_related(
                "locations",
                "characteristics"
            ),
            id=animal_id
        )

        serializer = AnimalDetailSerializer(animal)
        return Response(serializer.data)

class AnimalBatchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get("limit", 10))
        ordering = request.query_params.get("ordering", "random")

        if ordering == "alphabetical":
            queryset = (
                Animal.objects
                .prefetch_related('characteristics')
                .order_by("name")[:limit]
            )

        elif ordering == "random":
            # Fetch only PKs (integers) — cheap even for large tables
            all_pks = list(Animal.objects.values_list('pk', flat=True))
            if not all_pks:
                return Response([], status=200)

            sampled_pks = random.sample(all_pks, min(limit, len(all_pks)))
            queryset = (
                Animal.objects
                .prefetch_related('characteristics')
                .filter(pk__in=sampled_pks)
            )

        else:
            queryset = (
                Animal.objects
                .prefetch_related('characteristics')[:limit]
            )

        serializer = AnimalBasicSerializer(queryset, many=True)
        return Response(serializer.data)