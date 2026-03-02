
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
                "animallocation_set",
                "animalcharacteristic_set"
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

        queryset = Animal.objects.prefetch_related('animalcharacteristic_set').all()

        if ordering == "alphabetical":
            queryset = queryset.order_by("name")[:limit]

        elif ordering == "random":
            # Efficient random selection (avoid order_by("?"))
            total = queryset.count()
            if total == 0:
                return Response([], status=200)

            random_indices = random.sample(
                range(total),
                min(limit, total)
            )
            queryset = [queryset[i] for i in random_indices]

        else:
            queryset = queryset[:limit]

        serializer = AnimalBasicSerializer(queryset, many=True)
        return Response(serializer.data)