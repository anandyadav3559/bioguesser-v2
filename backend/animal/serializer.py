from rest_framework import serializers
from .models import Animal, AnimalLocation, AnimalCharacteristic

class AnimalCharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalCharacteristic
        fields = "__all__"


class AnimalBasicSerializer(serializers.ModelSerializer):
    characteristics = AnimalCharacteristicSerializer(
        source="animalcharacteristic_set",
        many=True,
        read_only=True
    )

    class Meta:
        model = Animal
        fields = ["id", "name", "scientific_name", "image_url", "characteristics"]


class AnimalLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalLocation
        fields = ["latitude", "longitude", "h3_index", "count"]


class AnimalDetailSerializer(serializers.ModelSerializer):
    locations = AnimalLocationSerializer(
        source="animallocation_set",
        many=True
    )
    characteristics = AnimalCharacteristicSerializer(
        source="animalcharacteristic_set",
        many=True
    )

    class Meta:
        model = Animal
        fields = [
            "id",
            "name",
            "scientific_name",
            "locations",
            "characteristics"
        ]