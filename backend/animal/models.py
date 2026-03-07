import uuid
from django.db import models


class Animal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    scientific_name = models.TextField(unique=True, null=True, blank=True)
    image_url = models.TextField(null=True, blank=True)
    max_probability = models.FloatField(null=True, blank=True)
    entropy = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "animals"


class AnimalLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name="locations",
        db_index=True
    )

    h3_index = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    count = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "animal_locations"


class AnimalCharacteristic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name="characteristics",
        db_index=True
    )

    prey = models.TextField(null=True, blank=True)
    gestation_period = models.TextField(null=True, blank=True)
    habitat = models.TextField(null=True, blank=True)
    predators = models.TextField(null=True, blank=True)
    average_litter_size = models.TextField(null=True, blank=True)
    top_speed = models.TextField(null=True, blank=True)
    lifespan = models.TextField(null=True, blank=True)
    weight = models.TextField(null=True, blank=True)
    length = models.TextField(null=True, blank=True)
    skin_type = models.TextField(null=True, blank=True)
    color = models.TextField(null=True, blank=True)
    age_of_sexual_maturity = models.TextField(null=True, blank=True)
    age_of_weaning = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "animal_characteristics"

